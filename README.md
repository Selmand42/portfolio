# Selman Demir - Portfolio Website

A modern, responsive personal portfolio website showcasing mathematical engineering, AI/ML expertise, and competitive programming achievements.

## 🚀 Live Features

- **Responsive Design**: Optimized for all device sizes
- **Modern UI/UX**: Navy-coral-gold color scheme with smooth animations
- **Interactive Elements**: Hover effects, scroll animations, and dynamic content
- **Contact Form**: Form validation with direct contact information
- **SEO Optimized**: Proper meta tags and semantic HTML structure
- **Professional Sections**: Skills, Certifications, Achievements, and Projects

## 📁 File Structure

```
├── index.html      # Main HTML file
├── styles.css      # CSS styles and responsive design
├── script.js       # JavaScript functionality
└── README.md       # Documentation
```

## 🎯 Portfolio Sections

### 1. **Hero Section**
- Professional introduction as Mathematical Engineering student
- Focus on AI-driven decision-making and algorithmic problem solving
- Profile photo integration with Google Drive support
- Call-to-action buttons

### 2. **About Section**
- Personal story focused on AI and algorithmic interests
- Professional summary highlighting technical journey
- Statistics and achievements summary

### 3. **Skills Section**
- **Programming Languages**: Python, C++, C, Java, Bash
- **AI & Data Science**: PyTorch, TensorFlow, Scikit-learn, OpenCV, Pandas, NumPy
- **Tools & Workflow**: Git, Linux, Google Colab, Jupyter Notebook, Kaggle, VS Code

### 4. **Certifications Section**
Real certifications with direct links:
- **Supervised Machine Learning**: Stanford & DeepLearning.ai
- **Advanced Learning Algorithms**: Stanford & DeepLearning.ai
- **Unsupervised Learning, Recommenders, RL**: Stanford & DeepLearning.ai
- **Intermediate Machine Learning**: Kaggle
- **Computer Vision**: Kaggle

### 5. **Achievements Section**
- **Competitive Programming**: LeetCode Global Rank 2,284 (Top 0.05%)
- **Contest Performance**: Top 4.1% in 30+ LeetCode contests
- **Consistency**: 300+ day streaks for two consecutive years
- **Academic Recognition**: 1st Place in 42 Istanbul Piscine

### 6. **Projects Section**
Organized by categories:
- **42 School Projects**: System programming and algorithms
- **AI & Data Science Projects**: Machine learning applications
- **General Development Projects**: Full-stack and automation tools

### 7. **Contact Section**
- Direct contact information for Istanbul, Turkey
- Social media links (LinkedIn, GitHub, LeetCode, Instagram)
- Contact form with validation (shows direct email for contact)

## 🎨 Design Features

### Color Scheme
- **Primary Navy**: #0f172a, #1e293b (Professional depth)
- **Coral Pink**: #f43f5e (Vibrant accent)
- **Ocean Blue**: #3b82f6 (Technical sophistication)
- **Gold**: #fbbf24, #f59e0b (Achievement highlights)

### Visual Elements
- **Gradient Backgrounds**: Multi-layered with texture overlays
- **Glass-morphism Effects**: Modern translucent cards
- **Smooth Animations**: Scroll-triggered and hover effects
- **Typography**: Inter font family for readability
- **Responsive Grid**: Flexible layouts for all devices

## 📱 Technical Implementation

### JavaScript Features
- **Mobile Navigation**: Hamburger menu for mobile devices
- **Smooth Scrolling**: Animated navigation between sections
- **Scroll Animations**: Elements animate as they come into view
- **Form Validation**: Input validation with user feedback
- **Counter Animations**: Animated statistics in achievements
- **Interactive Notifications**: Success/error message system

### CSS Features
- **CSS Grid & Flexbox**: Modern layout systems
- **Custom Properties**: Consistent color and spacing
- **Media Queries**: Responsive design for all screen sizes
- **Animations**: Keyframe animations and transitions
- **Gradient Effects**: Advanced gradient text and backgrounds

### Performance Optimizations
- **Efficient CSS**: Optimized selectors and minimal reflows
- **Lazy Loading**: Scroll-triggered animations
- **Minimal Dependencies**: Only Font Awesome and Google Fonts
- **Semantic HTML**: Proper structure for SEO and accessibility

## 🖼️ Profile Photo Setup

### Google Drive Integration
1. Upload your photo to Google Drive
2. Right-click → Share → "Anyone with the link can view"
3. Copy the file ID from the share URL
4. Update the image source in `index.html`:
```html
<img src="https://drive.google.com/thumbnail?id=YOUR_FILE_ID&sz=w1000"
     alt="Selman Demir" class="profile-photo">
```

### Alternative: Local Images
1. Create an `images` folder in your project
2. Save your photo as `profile.jpg`
3. Update HTML: `<img src="images/profile.jpg" alt="Selman Demir" class="profile-photo">`

## 📞 Contact Form

The contact form includes:
- **Input Validation**: Name, email, subject, and message validation
- **Email Format Check**: Regex validation for email addresses
- **User Feedback**: Error notifications for missing or invalid data
- **Direct Contact**: Shows direct email when form submission fails

**Note**: Form currently shows direct contact information instead of sending emails. To implement real email functionality, integrate with services like EmailJS, Formspree, or Netlify Forms.

## 🌐 Deployment Options

### GitHub Pages (Recommended)
1. Create a GitHub repository
2. Upload all files to the repository
3. Go to Settings → Pages
4. Select source branch (main)
5. Access at: `https://yourusername.github.io/repository-name`

### Netlify
1. Create a Netlify account
2. Drag and drop project folder
3. Instant deployment with custom domain support

### Vercel
1. Create a Vercel account
2. Import from GitHub repository
3. Automatic deployments on code changes

## 🔧 Customization Guide

### Adding New Sections
1. **HTML Structure**:
```html
<section id="new-section" class="new-section">
    <div class="container">
        <h2 class="section-title">New Section</h2>
        <!-- Content here -->
    </div>
</section>
```

2. **Navigation Link**:
```html
<li class="nav-item">
    <a href="#new-section" class="nav-link">New Section</a>
</li>
```

3. **CSS Styling**: Follow existing patterns in `styles.css`

### Updating Content
- **Personal Information**: Update hero section and about text
- **Skills**: Modify skill categories and tags
- **Certifications**: Add new certifications with valid links
- **Achievements**: Update with personal accomplishments
- **Projects**: Replace with your own project repositories

### Color Customization
Update CSS custom properties:
```css
:root {
    --primary-navy: #0f172a;
    --coral-pink: #f43f5e;
    --ocean-blue: #3b82f6;
    --gold: #fbbf24;
}
```

## 📊 Analytics Integration

Add tracking code before closing `</head>` tag:
```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

## 🚀 Performance Tips

1. **Image Optimization**: Use WebP format for better compression
2. **CDN Usage**: Consider using CDN for external resources
3. **Minification**: Minify CSS and JavaScript for production
4. **Lazy Loading**: Implement lazy loading for images
5. **Caching**: Set up proper cache headers on server

## 📱 Browser Support

- ✅ Chrome (recommended)
- ✅ Firefox
- ✅ Safari
- ✅ Edge
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

## 🔄 Updates & Maintenance

### Regular Updates
- **Content**: Keep certifications and achievements current
- **Dependencies**: Update Font Awesome and Google Fonts links
- **Security**: Monitor for any security updates
- **Performance**: Regular performance audits

### Version Control
- Use Git for version control
- Create branches for major updates
- Tag releases for stable versions

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Feel free to fork this project and make improvements. Suggestions and feedback are welcome!

---

**Portfolio of Selman Demir** - Mathematical Engineering Student at Istanbul Technical University & Software Development Trainee at 42 Istanbul

🔗 **Links**: [LinkedIn](https://www.linkedin.com/in/selman-demir-107958227/) | [GitHub](https://github.com/Selmand42) | [LeetCode](https://leetcode.com/u/Selmand42/) | [Email](mailto:demirmuha21@itu.edu.tr)
