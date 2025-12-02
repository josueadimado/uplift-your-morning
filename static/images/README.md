# Images Directory Guide

This directory contains all static images for the UPLIFT Afrika website.

## Directory Structure

```
static/
└── images/
    ├── logo/          # Logos and branding images
    ├── general/       # General images (hero images, banners, etc.)
    └── icons/         # Icons and small graphics
```

## Where to Put Your Images

### Logos
Put your logo files in: `static/images/logo/`
- Recommended formats: PNG (with transparency) or SVG
- Recommended name: `logo.png` or `logo.svg`
- The base template will automatically use `logo.png` if it exists

### General Images
Put general images in: `static/images/general/`
- Hero images, banners, background images
- Photos for pages, testimonies, etc.
- Any other general-purpose images

### Icons
Put icons in: `static/images/icons/`
- Small graphics, icons, badges
- Social media icons, etc.

## How to Use Images in Templates

### 1. Load static files at the top of your template:
```django
{% load static %}
```

### 2. Use images in your HTML:
```django
<!-- Logo -->
<img src="{% static 'images/logo/logo.png' %}" alt="UPLIFT Afrika Logo">

<!-- General image -->
<img src="{% static 'images/general/hero-image.jpg' %}" alt="Hero Image">

<!-- Icon -->
<img src="{% static 'images/icons/facebook-icon.png' %}" alt="Facebook">
```

### 3. Example with styling (Tailwind CSS):
```django
<img src="{% static 'images/logo/logo.png' %}" 
     alt="UPLIFT Afrika Logo" 
     class="h-12 w-auto">
```

## Image Formats

- **PNG**: Best for logos and images with transparency
- **JPG/JPEG**: Best for photos (smaller file size)
- **SVG**: Best for logos and icons (scalable, small file size)
- **WebP**: Modern format (smaller, better quality) - supported by most browsers

## Tips

1. **Optimize images**: Compress images before uploading to reduce page load time
2. **Use descriptive names**: `hero-image.jpg` is better than `img1.jpg`
3. **Alt text**: Always include alt text for accessibility
4. **Responsive images**: Use Tailwind classes like `w-full` or `max-w-md` for responsive sizing

## Media Files vs Static Files

- **Static files** (this directory): Images that are part of your website design (logos, icons, default images)
- **Media files** (`media/` directory): User-uploaded content (devotion PDFs, resource files, user-submitted images)

Static files are version-controlled and part of your codebase.
Media files are uploaded by users/admins and stored separately.

