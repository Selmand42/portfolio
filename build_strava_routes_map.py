#!/usr/bin/env python3
"""
Strava API'den aktiviteleri çekip varsayılan olarak `strava_routes_map.html` haritasını üretir;
aynı klasörde `index.html` varsa spor bölümündeki Strava özet sayılarını da günceller.

Gerekli paketler (ör. sanal ortam):
  python3 -m venv .venv && source .venv/bin/activate
  pip install -r requirements.txt

Ortam değişkenleri (.env, betiğin klasöründe) — yalnızca şu üçünü tanımlamanız yeterli:
  STRAVA_CLIENT_ID
  STRAVA_CLIENT_SECRET
  STRAVA_REFRESH_TOKEN
  (Betiğin refresh token ile geçici access token alması için başka bir satır gerekmez.)

İsteğe bağlı — .env’de olmasa da çalışır (varsayılanlar kullanılır):
  STRAVA_ACCESS_TOKEN     Refresh yerine doğrudan token (nadiren)
  STRAVA_MAP_CENTER_LAT, STRAVA_MAP_CENTER_LON, STRAVA_MAP_START_ZOOM, STRAVA_MAP_GEOCODE_ZOOM
  STRAVA_OUTPUT_HTML
  STRAVA_USE_CARTO_VOYAGER=1  veya --use-carto-voyager  (Carto Voyager tabanı; orijinal HTML OSM kullanır)
  STRAVA_USE_OSM_TILES=1  (eski) OSM’yi açıkça tercih eder; Carto ortam bayrağıyla birlikteyse OSM önceliklidir
  --use-osm-tiles  Eski CLI bayrağı; Voyager seçili olsa bile OSM kullanılır
  STRAVA_INDEX_HTML  veya --index-html YOL  Farklı bir index.html yolu (boş bırakılırsa betik klasöründeki dosya kullanılır)
  --no-update-index  Aynı klasörde index.html olsa bile Strava sayılarını yazma

Tek klasörde (bu proje): yalnızca betiği çalıştırmanız yeterli; harita + index güncellenir.

Günlük otomasyon (macOS): launchd ile yukarıdaki komutu çalıştırın; ardından git commit/push kendi akışınıza göre.
GitHub Actions: aynı komutu bir workflow’da çalıştırıp STRAVA_* sırlarını repo Secrets’ta tutun; çıktıları otomatik commit eden bir adım ekleyebilirsiniz.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import time
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests
from dotenv import load_dotenv

import folium
import folium.folium as _folium_core
import folium.plugins.fullscreen as _folium_fullscreen
from branca.element import Element, MacroElement
from folium.plugins import Fullscreen, Geocoder, MarkerCluster, MiniMap
from folium.template import Template

# repo/strava_routes_map.html ile aynı CDN / sıra (jQuery 1.12, Bootstrap 3 CSS, fullscreen 1.4.2)
_ATTR_OSM = (
    'Data by &copy; <a target="_blank" href="http://openstreetmap.org">OpenStreetMap</a>, '
    'under <a target="_blank" href="http://www.openstreetmap.org/copyright">ODbL</a>.'
)
_ATTR_STAMEN_TERRAIN = (
    'Map tiles by <a target="_blank" href="http://stamen.com">Stamen Design</a>, '
    'under <a target="_blank" href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>. '
    'Data by &copy; <a target="_blank" href="http://openstreetmap.org">OpenStreetMap</a>, '
    'under <a target="_blank" href="http://creativecommons.org/licenses/by-sa/3.0">CC BY SA</a>.'
)
_ATTR_STAMEN_TONER = (
    'Map tiles by <a target="_blank" href="http://stamen.com">Stamen Design</a>, '
    'under <a target="_blank" href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>. '
    'Data by &copy; <a target="_blank" href="http://openstreetmap.org">OpenStreetMap</a>, '
    'under <a target="_blank" href="http://www.openstreetmap.org/copyright">ODbL</a>.'
)
_ATTR_CARTO = (
    '&copy; <a target="_blank" href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> '
    'contributors &copy; <a target="_blank" href="http://cartodb.com/attributions">CartoDB</a>, '
    'CartoDB <a target="_blank" href ="http://cartodb.com/attributions">attributions</a>'
)
# strava_routes_map.html ile aynı: varsayılan taban OpenStreetMap raster
_URL_OSM_TILES = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
# İsteğe bağlı: dosya:// veya OSM tile engeli için Carto Voyager (görünüm orijinalden farklıdır)
_URL_CARTO_VOYAGER = "https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png"
# Voyager katmanı için attribution (OSM metni + CARTO)
_ATTR_SAFE_BASEMAP = (
    'Data by &copy; <a target="_blank" href="http://openstreetmap.org">OpenStreetMap</a>, '
    'under <a target="_blank" href="http://www.openstreetmap.org/copyright">ODbL</a>. '
    '&copy; <a target="_blank" href="https://carto.com/attributions">CARTO</a>'
)


def _env_truthy(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in ("1", "true", "yes", "on")


def _verify_map_html(out: Path, *, use_osm_tiles: bool) -> None:
    """strava/strava_routes_map.html ile aynı teknik omurgayı kontrol et (yaklaşık)."""
    if not out.is_file():
        return
    text = out.read_text(encoding="utf-8", errors="replace")
    checks = [
        ("https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/leaflet.js", "Leaflet 1.9.3"),
        ("https://code.jquery.com/jquery-1.12.4.min.js", "jQuery 1.12.4"),
        ("bootstrap/3.0.0/css/bootstrap.min.css", "Bootstrap 3 CSS"),
        ("leaflet.fullscreen/1.4.2/Control.FullScreen.min.js", "Fullscreen 1.4.2"),
        ("stamen-tiles-", "Stamen Terrain/Toner"),
        ("cartodb-basemaps-", "Carto Light/Dark (fastly)"),
        (".leaflet-control-geocoder", "Geocoder üst orta CSS"),
        ("L.control.scale()", "Ölçek çubuğu"),
        ("L.control.layers(", "Katman seçici"),
        ("L.Control.MiniMap", "Mini harita"),
    ]
    for needle, label in checks:
        if needle not in text:
            print(f"Uyarı: {label} — beklenen parça: {needle!r}", file=sys.stderr)
    if use_osm_tiles:
        if "tile.openstreetmap.org" not in text:
            print("Uyarı: OSM kiremiti açık ama tile.openstreetmap.org bulunamadı.", file=sys.stderr)
    else:
        if "basemaps.cartocdn.com/rastertiles/voyager" not in text:
            print("Uyarı: Güvenli Voyager tabanı URL'si bulunamadı.", file=sys.stderr)
        if text.count("tile.openstreetmap.org") > 0:
            print(
                "Uyarı: HTML içinde tile.openstreetmap.org geçiyor; "
                "katman menüsünden OSM seçilirse bloklanabilir.",
                file=sys.stderr,
            )


def _patch_folium_assets_to_match_repo_html() -> None:
    """Folium varsayılanlarını `repo/strava_routes_map.html` ile hizala (tek seferlik)."""
    _folium_core._default_js = [
        ("leaflet", "https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/leaflet.js"),
        ("jquery", "https://code.jquery.com/jquery-1.12.4.min.js"),
        (
            "bootstrap",
            "https://cdn.jsdelivr.net/npm/bootstrap@5.2.2/dist/js/bootstrap.bundle.min.js",
        ),
        (
            "awesome_markers",
            "https://cdnjs.cloudflare.com/ajax/libs/Leaflet.awesome-markers/2.0.2/leaflet.awesome-markers.js",
        ),
    ]
    _folium_core._default_css = [
        ("leaflet_css", "https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/leaflet.css"),
        (
            "bootstrap_css",
            "https://cdn.jsdelivr.net/npm/bootstrap@5.2.2/dist/css/bootstrap.min.css",
        ),
        (
            "bootstrap3_css",
            "https://netdna.bootstrapcdn.com/bootstrap/3.0.0/css/bootstrap.min.css",
        ),
        (
            "awesome_markers_font_css",
            "https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.2.0/css/all.min.css",
        ),
        (
            "awesome_markers_css",
            "https://cdnjs.cloudflare.com/ajax/libs/Leaflet.awesome-markers/2.0.2/leaflet.awesome-markers.css",
        ),
        (
            "awesome_rotate_css",
            "https://cdn.jsdelivr.net/gh/python-visualization/folium/"
            "folium/templates/leaflet.awesome.rotate.min.css",
        ),
    ]
    _folium_core.Map.default_js = _folium_core._default_js
    _folium_core.Map.default_css = _folium_core._default_css

    _folium_fullscreen.Fullscreen.default_js = [
        (
            "Control.FullScreen.min.js",
            "https://cdnjs.cloudflare.com/ajax/libs/leaflet.fullscreen/1.4.2/Control.FullScreen.min.js",
        )
    ]
    _folium_fullscreen.Fullscreen.default_css = [
        (
            "Control.FullScreen.min.css",
            "https://cdnjs.cloudflare.com/ajax/libs/leaflet.fullscreen/1.4.2/Control.FullScreen.min.css",
        )
    ]


_patch_folium_assets_to_match_repo_html()


class _RemoveOtherBasemaps(MacroElement):
    """`repo/strava_routes_map.html`: LayerControl sonrası ek OSM/Stamen/Carto tabanlarını haritadan kaldır."""

    _template = Template(
        """
        {% macro script(this, kwargs) %}
            {% for nm in this.tile_js_names %}
            {{ nm }}.remove();
            {% endfor %}
        {% endmacro %}
        """
    )

    def __init__(self, tile_layers: List[folium.raster_layers.TileLayer]) -> None:
        super().__init__()
        self._name = "RemoveExtraBasemaps"
        self.tile_js_names = [lyr.get_name() for lyr in tile_layers]


STRAVA_TOKEN_URL = "https://www.strava.com/oauth/token"
STRAVA_API = "https://www.strava.com/api/v3"

# Orijinal HTML ile uyumlu rota renkleri ve Folium katman adları
ROUTE_STYLE = {"weight": 5, "opacity": 0.85}

RUN_TYPES = {"Run", "TrailRun", "VirtualRun"}
RIDE_TYPES = {
    "Ride",
    "EBikeRide",
    "EMountainBikeRide",
    "GravelRide",
    "MountainBikeRide",
    "Velomobile",
    "VirtualRide",
}
WALK_TYPES = {"Walk", "Hike"}
SOCCER_TYPES = {"Soccer", "Football"}
SWIM_TYPES = {"Swim"}
GYM_TYPES = {
    "WeightTraining",
    "Workout",
    "Crossfit",
    "Elliptical",
    "StairStepper",
}
BOULDER_TYPES = {"RockClimbing"}

# Strava’da süre kaydı olmayan salon seansları: gym kartı + Total Activities sayısına eklenir.
PORTFOLIO_GYM_ACTIVITY_COUNT_EXTRA = 31


def decode_polyline(polyline_str: str) -> List[Tuple[float, float]]:
    """Google encoded polyline -> [(lat, lon), ...]"""
    if not polyline_str:
        return []
    index, lat, lng = 0, 0, 0
    coordinates: List[Tuple[float, float]] = []
    strlen = len(polyline_str)
    while index < strlen:
        shift, result = 0, 0
        while True:
            b = ord(polyline_str[index]) - 63
            index += 1
            result |= (b & 0x1F) << shift
            shift += 5
            if b < 0x20:
                break
        dlat = ~(result >> 1) if (result & 1) else (result >> 1)
        lat += dlat
        shift, result = 0, 0
        while True:
            b = ord(polyline_str[index]) - 63
            index += 1
            result |= (b & 0x1F) << shift
            shift += 5
            if b < 0x20:
                break
        dlng = ~(result >> 1) if (result & 1) else (result >> 1)
        lng += dlng
        coordinates.append((lat * 1e-5, lng * 1e-5))
    return coordinates


def classify_activity(act: Dict[str, Any]) -> str:
    t = act.get("type") or act.get("sport_type") or ""
    if t in RUN_TYPES:
        return "run"
    if t in RIDE_TYPES:
        return "ride"
    if t in WALK_TYPES:
        return "walk"
    if t in SOCCER_TYPES:
        return "soccer"
    if t in SWIM_TYPES:
        return "swim"
    if t in GYM_TYPES:
        return "gym"
    if t in BOULDER_TYPES:
        return "bouldering"
    return "other"


def route_color(group: str) -> str:
    return {
        "run": "red",
        "ride": "blue",
        "walk": "green",
        "soccer": "gray",
        "swim": "cadetblue",
        "gym": "darkorange",
        "bouldering": "saddlebrown",
        "other": "purple",
    }[group]


def marker_icon_name(group: str) -> str:
    return {
        "run": "running",
        "ride": "bicycle",
        "walk": "walking",
        "soccer": "futbol",
        "swim": "person-swimming",
        "gym": "dumbbell",
        "bouldering": "mountain",
        "other": "map-marker",
    }[group]


def fmt_space_int(m: float) -> str:
    """Ör. 18714 -> '18 714' (binlik ayraç boşluk)."""
    n = int(round(m))
    return f"{n:,}".replace(",", " ")


def fmt_moving_time(total_seconds: float) -> str:
    """Strava `moving_time` (saniye) -> 1h 30m, 45m, 90s."""
    s = max(0, int(round(total_seconds)))
    if s == 0:
        return "0m"
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    if h:
        return f"{h}h {m}m" if m else f"{h}h"
    if m:
        return f"{m}m"
    return f"{sec}s"


def aggregate_sports_stats(activities: List[Dict[str, Any]]) -> Dict[str, Any]:
    """index.html spor kartları ile aynı sınıflandırma; Walk portföyde yok, sayıları `other` içine aktarılır."""
    keys = ("run", "ride", "soccer", "swim", "gym", "bouldering", "other")
    groups: Dict[str, Dict[str, float]] = {
        k: {"count": 0, "distance_m": 0.0, "elevation_m": 0.0, "moving_time_s": 0.0} for k in keys
    }
    total_distance_m = 0.0
    total_elevation_m = 0.0
    for act in activities:
        g = classify_activity(act)
        if g == "walk":
            g = "other"
        d = float(act.get("distance") or 0.0)
        eg = act.get("total_elevation_gain")
        el = float(eg) if eg is not None else 0.0
        mt = float(act.get("moving_time") or 0.0)
        total_distance_m += d
        total_elevation_m += el
        groups[g]["count"] += 1
        groups[g]["distance_m"] += d
        groups[g]["elevation_m"] += el
        groups[g]["moving_time_s"] += mt
    out_groups: Dict[str, Dict[str, Any]] = {}
    for k in keys:
        c = int(groups[k]["count"])
        dm = groups[k]["distance_m"]
        em = groups[k]["elevation_m"]
        mv = float(groups[k]["moving_time_s"])
        out_groups[k] = {
            "count": c,
            "distance_km": dm / 1000.0,
            "elevation_m": em,
            "moving_time_s": mv,
        }
    return {
        "activity_count": len(activities),
        "total_distance_km": total_distance_m / 1000.0,
        "total_elevation_m": total_elevation_m,
        "groups": out_groups,
    }


def _get_element_inner_by_id(html: str, tag: str, elem_id: str) -> Optional[str]:
    pat = re.compile(
        rf'<{tag}\b[^>]*\bid="{re.escape(elem_id)}"[^>]*>([^<]*)</{tag}\s*>',
        re.IGNORECASE,
    )
    m = pat.search(html)
    return m.group(1).strip() if m else None


def _build_stats_note(html: str) -> str:
    """Önceki içerikteki 'since …' ifadesini koru; ardından güncel senkron satırını ekle."""
    old = _get_element_inner_by_id(html, "span", "strava-stats-note") or ""
    since_m = re.search(r"\bsince\b[^·]*", old, flags=re.IGNORECASE)
    since_part = since_m.group(0).strip() if since_m else ""
    if since_part:
        since_part = re.sub(r"\s+", " ", since_part)
    today_s = f"Last updated {date.today().strftime('%d-%m-%Y')} (Strava sync)"
    if since_part:
        return f"{since_part} · {today_s}"
    return today_s


def _replace_by_element_id(html: str, tag: str, elem_id: str, new_inner: str) -> str:
    pat = re.compile(
        rf'(<{tag}\b[^>]*\bid="{re.escape(elem_id)}"[^>]*>)([^<]*)(</{tag}\s*>)',
        re.IGNORECASE,
    )
    if not pat.search(html):
        raise ValueError(f'index.html içinde <{tag} id="{elem_id}"> bulunamadı')

    def _repl(m: re.Match) -> str:
        return m.group(1) + new_inner + m.group(3)

    return pat.sub(_repl, html, count=1)


def patch_portfolio_index_html(path: Path, stats: Dict[str, Any]) -> None:
    """`repo/index.html` içindeki `id="strava-*"` alanlarını API ile uyumlu doldurur."""
    html = path.read_text(encoding="utf-8")
    note = _build_stats_note(html)
    g = stats["groups"]
    html = _replace_by_element_id(html, "h3", "strava-total-km", f"{stats['total_distance_km']:.2f} km")
    html = _replace_by_element_id(
        html, "h3", "strava-total-elev", f"{fmt_space_int(stats['total_elevation_m'])} m"
    )
    total_activities_display = int(stats["activity_count"]) + PORTFOLIO_GYM_ACTIVITY_COUNT_EXTRA
    html = _replace_by_element_id(html, "h3", "strava-total-count", str(total_activities_display))
    html = _replace_by_element_id(html, "span", "strava-stats-note", note)
    for key, prefix in (
        ("run", "strava-run"),
        ("soccer", "strava-soccer"),
        ("ride", "strava-ride"),
        ("swim", "strava-swim"),
        ("gym", "strava-gym"),
        ("bouldering", "strava-bouldering"),
    ):
        s = g[key]
        act_count = int(s["count"])
        if key == "gym":
            act_count += PORTFOLIO_GYM_ACTIVITY_COUNT_EXTRA
        html = _replace_by_element_id(html, "span", f"{prefix}-activities", str(act_count))
        if key in ("gym", "bouldering"):
            html = _replace_by_element_id(
                html, "span", f"{prefix}-time", fmt_moving_time(float(s["moving_time_s"]))
            )
        else:
            html = _replace_by_element_id(
                html, "span", f"{prefix}-distance", f"{s['distance_km']:.2f} km"
            )
        html = _replace_by_element_id(
            html, "span", f"{prefix}-elevation", f"{fmt_space_int(s['elevation_m'])} m"
        )
    path.write_text(html, encoding="utf-8")


def refresh_access_token(client_id: str, client_secret: str, refresh_token: str) -> str:
    r = requests.post(
        STRAVA_TOKEN_URL,
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        },
        timeout=60,
    )
    r.raise_for_status()
    data = r.json()
    token = data.get("access_token")
    if not token:
        raise RuntimeError(f"Token yanıtında access_token yok: {data}")
    return str(token)


def fetch_all_activities(access_token: str, per_page: int = 200) -> List[Dict[str, Any]]:
    headers = {"Authorization": f"Bearer {access_token}"}
    out: List[Dict[str, Any]] = []
    page = 1
    while True:
        r = requests.get(
            f"{STRAVA_API}/athlete/activities",
            headers=headers,
            params={"page": page, "per_page": per_page},
            timeout=120,
        )
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        out.extend(batch)
        if len(batch) < per_page:
            break
        page += 1
        # Strava hız limiti: kaba bir gecikme
        time.sleep(0.2)
    return out


def popup_html(act: Dict[str, Any]) -> str:
    name = act.get("name") or "İsimsiz"
    typ = act.get("type") or act.get("sport_type") or ""
    date = (act.get("start_date_local") or "")[:10]
    dist_km = (act.get("distance") or 0) / 1000.0
    elev = act.get("total_elevation_gain")
    elev_s = f"{elev:.0f} m" if elev is not None else "—"
    return (
        f"         <b>{name}</b><br>         Type: {typ}<br>         "
        f"Date: {date}<br>         Distance: {dist_km:.2f} km<br>         "
        f"Elevation: {elev_s}         "
    )


def tooltip_text(act: Dict[str, Any]) -> str:
    name = act.get("name") or "İsimsiz"
    typ = act.get("type") or act.get("sport_type") or ""
    dist_km = (act.get("distance") or 0) / 1000.0
    return f"                     {name} ({typ}, {dist_km:.2f} km)                 "


def add_geocoder_style(m: folium.Map) -> None:
    """Orijinal HTML ile aynı: adres arama kutusu üstte ortada."""
    m.get_root().header.add_child(
        Element(
            """
            <style>
            .leaflet-control-geocoder {
                position: fixed !important;
                top: 10px !important;
                left: 50% !important;
                transform: translateX(-50%) !important;
                z-index: 1000 !important;
            }
            </style>
            """
        )
    )


def build_map(
    activities: List[Dict[str, Any]],
    center: Tuple[float, float],
    start_zoom: int,
    geocode_zoom: int,
    *,
    use_osm_tiles: bool = True,
) -> folium.Map:
    m = folium.Map(
        location=[center[0], center[1]],
        zoom_start=start_zoom,
        zoom_control=True,
        tiles=None,
        control_scale=True,
    )
    add_geocoder_style(m)

    base_url = _URL_OSM_TILES if use_osm_tiles else _URL_CARTO_VOYAGER
    base_attr = _ATTR_OSM if use_osm_tiles else _ATTR_SAFE_BASEMAP

    # strava_routes_map.html: iki adet aynı taban + remove; varsayılan URL OSM (orijinal ile aynı)
    tile_osm_1 = folium.TileLayer(
        tiles=base_url,
        attr=base_attr,
        max_zoom=18,
        max_native_zoom=18,
        name="openstreetmap",
    )
    tile_osm_1.add_to(m)

    tile_osm_2 = folium.TileLayer(
        tiles=base_url,
        attr=base_attr,
        max_zoom=18,
        max_native_zoom=18,
        name="OpenStreetMap",
    )
    tile_osm_2.add_to(m)

    tile_terrain = folium.TileLayer(
        tiles="https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}.jpg",
        attr=_ATTR_STAMEN_TERRAIN,
        max_zoom=18,
        max_native_zoom=18,
        name="Terrain",
    )
    tile_terrain.add_to(m)

    tile_toner = folium.TileLayer(
        tiles="https://stamen-tiles-{s}.a.ssl.fastly.net/toner/{z}/{x}/{y}.png",
        attr=_ATTR_STAMEN_TONER,
        max_zoom=18,
        max_native_zoom=18,
        name="Toner",
    )
    tile_toner.add_to(m)

    tile_light = folium.TileLayer(
        tiles="https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png",
        attr=_ATTR_CARTO,
        max_zoom=18,
        max_native_zoom=18,
        name="Light",
    )
    tile_light.add_to(m)

    tile_dark = folium.TileLayer(
        tiles="https://cartodb-basemaps-{s}.global.ssl.fastly.net/dark_all/{z}/{x}/{y}.png",
        attr=_ATTR_CARTO,
        max_zoom=18,
        max_native_zoom=18,
        name="Dark",
    )
    tile_dark.add_to(m)

    prepared: List[Tuple[str, Dict[str, Any], List[Tuple[float, float]]]] = []
    for act in activities:
        msummary = (act.get("map") or {}).get("summary_polyline")
        if not msummary:
            continue
        coords = decode_polyline(msummary)
        if len(coords) < 2:
            continue
        prepared.append((classify_activity(act), act, coords))

    present = {g for g, _, _ in prepared}
    overlay_order = [
        "ride",
        "run",
        "soccer",
        "walk",
        "swim",
        "gym",
        "bouldering",
        "other",
    ]
    used_groups = [k for k in overlay_order if k in present]
    layer_labels = {
        "run": ("Run Routes", "Run Start/End Points"),
        "ride": ("Ride Routes", "Ride Start/End Points"),
        "walk": ("Walk Routes", "Walk Start/End Points"),
        "soccer": ("Soccer Routes", "Soccer Start/End Points"),
        "swim": ("Swim Routes", "Swim Start/End Points"),
        "gym": ("Gym Routes", "Gym Start/End Points"),
        "bouldering": ("Bouldering Routes", "Bouldering Start/End Points"),
        "other": ("Other Routes", "Other Start/End Points"),
    }
    groups: Dict[str, folium.FeatureGroup] = {}
    clusters: Dict[str, MarkerCluster] = {}
    for grp in used_groups:
        rlabel, clabel = layer_labels[grp]
        groups[grp] = folium.FeatureGroup(name=rlabel)
        clusters[grp] = MarkerCluster(name=clabel)
        groups[grp].add_to(m)
        clusters[grp].add_to(m)

    for grp, act, coords in prepared:
        color = route_color(grp)
        line = folium.PolyLine(
            locations=[[lat, lon] for lat, lon in coords],
            color=color,
            **ROUTE_STYLE,
        )
        line.add_child(folium.Popup(popup_html(act), max_width=350))
        line.add_child(folium.Tooltip(tooltip_text(act), sticky=True))
        line.add_to(groups[grp])

        icon_name = marker_icon_name(grp)
        name = act.get("name") or "İsimsiz"

        folium.Marker(
            location=[coords[0][0], coords[0][1]],
            popup=f"Start: {name}",
            tooltip=f"Start: {name}",
            icon=folium.Icon(color="green", icon=icon_name, prefix="fa"),
        ).add_to(clusters[grp])

        folium.Marker(
            location=[coords[-1][0], coords[-1][1]],
            popup=f"End: {name}",
            tooltip=f"End: {name}",
            icon=folium.Icon(color="red", icon=icon_name, prefix="fa"),
        ).add_to(clusters[grp])

    folium.LayerControl(collapsed=True, position="topright").add_to(m)

    # Orijinal HTML: katman seçiciden sonra yalnızca ilk OSM haritada kalsın (JS tile değişkenleri tanımlı iken)
    _RemoveOtherBasemaps(
        [tile_osm_2, tile_terrain, tile_toner, tile_light, tile_dark]
    ).add_to(m)

    Fullscreen(
        position="topleft",
        title="Full Screen",
        title_cancel="Exit Full Screen",
        force_separate_button=False,
    ).add_to(m)

    # Ana haritadaki TileLayer ile aynı JS değişkenine tekrar `var` yazılmasın diye ayrı örnek
    mini_basemap = folium.TileLayer(
        tiles=base_url,
        attr=base_attr,
        max_zoom=18,
        max_native_zoom=18,
    )
    MiniMap(
        tile_layer=mini_basemap,
        zoom_level_offset=-5,
        width=150,
        height=150,
        collapsed_width=25,
        collapsed_height=25,
        toggle_display=True,
        zoom_animation=False,
        auto_toggle_display=False,
        center_fixed=False,
        minimized=False,
    ).add_to(m)

    Geocoder(
        collapsed=False,
        position="topright",
        add_marker=True,
        zoom=geocode_zoom,
    ).add_to(m)

    return m


def main() -> int:
    parser = argparse.ArgumentParser(description="Strava rotalarından Folium HTML haritası üret.")
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Çıktı HTML dosyası (varsayılan: STRAVA_OUTPUT_HTML veya strava_routes_map.html)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Sadece ortamı doğrula, haritayı kaydetme.",
    )
    parser.add_argument(
        "--use-carto-voyager",
        action="store_true",
        help="Varsayılan yerine Carto Voyager tabanı (orijinal HTML’den farklı renk paleti).",
    )
    parser.add_argument(
        "--use-osm-tiles",
        action="store_true",
        help="Eski seçenek: varsayılan zaten OSM; Voyager ile birlikte kullanılırsa OSM önceliklidir.",
    )
    parser.add_argument(
        "--index-html",
        default=None,
        metavar="PATH",
        help="Strava özet sayıları (id=strava-*): yol verilmezse betik klasöründe index.html aranır.",
    )
    parser.add_argument(
        "--no-update-index",
        action="store_true",
        help="index.html içindeki Strava sayılarını güncelleme.",
    )
    args = parser.parse_args()

    base = Path(__file__).resolve().parent
    load_dotenv(base / ".env")

    client_id = os.environ.get("STRAVA_CLIENT_ID", "").strip()
    client_secret = os.environ.get("STRAVA_CLIENT_SECRET", "").strip()
    refresh_token = os.environ.get("STRAVA_REFRESH_TOKEN", "").strip()
    access_token = os.environ.get("STRAVA_ACCESS_TOKEN", "").strip()

    if refresh_token and client_id and client_secret:
        access_token = refresh_access_token(client_id, client_secret, refresh_token)
    elif not access_token:
        print(
            "Hata: STRAVA_REFRESH_TOKEN + STRAVA_CLIENT_ID + STRAVA_CLIENT_SECRET "
            "veya STRAVA_ACCESS_TOKEN gerekli.",
            file=sys.stderr,
        )
        return 1

    center_lat = float(os.environ.get("STRAVA_MAP_CENTER_LAT", "41.0082"))
    center_lon = float(os.environ.get("STRAVA_MAP_CENTER_LON", "28.9784"))
    start_zoom = int(os.environ.get("STRAVA_MAP_START_ZOOM", "11"))
    geocode_zoom = int(os.environ.get("STRAVA_MAP_GEOCODE_ZOOM", str(start_zoom)))
    out_name = args.output or os.environ.get("STRAVA_OUTPUT_HTML", "strava_routes_map.html")
    out_path = Path(out_name)
    if not out_path.is_absolute():
        out_path = base / out_path

    if args.dry_run:
        print("Ortam tamam, dry-run: harita üretilmedi.")
        return 0

    acts = fetch_all_activities(access_token)
    with_poly = sum(1 for a in acts if (a.get("map") or {}).get("summary_polyline"))
    print(f"Toplam aktivite: {len(acts)}, polyline olan: {with_poly}")

    stats = aggregate_sports_stats(acts)

    use_voyager = args.use_carto_voyager or _env_truthy("STRAVA_USE_CARTO_VOYAGER")
    if args.use_osm_tiles or _env_truthy("STRAVA_USE_OSM_TILES"):
        use_voyager = False
    use_osm = not use_voyager
    m = build_map(
        acts,
        (center_lat, center_lon),
        start_zoom,
        geocode_zoom,
        use_osm_tiles=use_osm,
    )
    m.save(str(out_path))
    _verify_map_html(out_path, use_osm_tiles=use_osm)
    print(f"Kaydedildi: {out_path}")

    idx_path: Optional[Path] = None
    index_arg = (args.index_html if args.index_html is not None else "").strip()
    if not index_arg:
        index_arg = (os.environ.get("STRAVA_INDEX_HTML", "") or "").strip()
    if index_arg:
        idx_path = Path(index_arg)
        if not idx_path.is_absolute():
            idx_path = base / idx_path
    elif not args.no_update_index:
        candidate = base / "index.html"
        if candidate.is_file():
            idx_path = candidate

    if idx_path is not None:
        if not idx_path.is_file():
            print(f"Hata: index.html bulunamadı: {idx_path}", file=sys.stderr)
            return 1
        patch_portfolio_index_html(idx_path, stats)
        print(f"index.html güncellendi: {idx_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
