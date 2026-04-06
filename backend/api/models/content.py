"""
Content Models for VynilArt API
"""
from django.db import models
from django.utils.text import slugify


class BlogCategory(models.Model):
    """
    Blog post categories
    """
    name_ar = models.CharField(max_length=255)
    name_en = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, null=True)
    
    # SEO and metadata
    meta_title = models.CharField(max_length=255, blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)
    
    # Visual
    image = models.CharField(max_length=500, blank=True, null=True)
    color = models.CharField(max_length=7, blank=True, null=True)  # Hex color
    
    # Organization
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
            models.Index(fields=['sort_order']),
        ]
        ordering = ['sort_order', 'name_ar']
        verbose_name = 'Blog Category'
        verbose_name_plural = 'Blog Categories'

    def __str__(self):
        return self.name_ar

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_en)
        super().save(*args, **kwargs)

    @property
    def post_count(self):
        """Count of published posts in this category"""
        return self.posts.filter(is_published=True).count()


class BlogPost(models.Model):
    """
    Blog posts with multilingual content
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('scheduled', 'Scheduled'),
        ('archived', 'Archived'),
    ]
    
    # Basic information
    title_ar = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    
    # Content
    content_ar = models.TextField()
    content_en = models.TextField()
    summary_ar = models.TextField(blank=True, null=True)
    summary_en = models.TextField(blank=True, null=True)
    
    # Categorization
    category = models.ForeignKey(
        BlogCategory, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='posts'
    )
    tags = models.JSONField(default=list, blank=True)
    
    # Author and attribution
    author = models.ForeignKey(
        'api_user.User', 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='blog_posts'
    )
    guest_author = models.CharField(max_length=255, blank=True, null=True)
    
    # Media
    featured_image = models.CharField(max_length=500, blank=True, null=True)
    gallery_images = models.JSONField(
        default=list,
        help_text="List of additional image URLs"
    )
    
    # SEO and metadata
    meta_title = models.CharField(max_length=255, blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)
    meta_keywords = models.JSONField(default=list, blank=True)
    focus_keyword = models.CharField(max_length=100, blank=True, null=True)
    
    # Publishing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    is_top_story = models.BooleanField(default=False)
    
    # Analytics
    views = models.IntegerField(default=0)
    read_time = models.IntegerField(default=0)  # Estimated reading time in minutes
    shares = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    
    # Scheduling
    published_at = models.DateTimeField(blank=True, null=True)
    
    # Comments settings
    comments_enabled = models.BooleanField(default=True)
    comments_require_approval = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['status']),
            models.Index(fields=['category']),
            models.Index(fields=['author']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['is_top_story']),
            models.Index(fields=['published_at']),
            models.Index(fields=['views']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title_ar

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title_en)
        
        # Auto-generate summaries if not provided
        if not self.summary_ar and self.content_ar:
            self.summary_ar = self.content_ar[:200] + '...' if len(self.content_ar) > 200 else self.content_ar
        if not self.summary_en and self.content_en:
            self.summary_en = self.content_en[:200] + '...' if len(self.content_en) > 200 else self.content_en
        
        # Auto-calculate reading time (assuming 200 words per minute)
        word_count = len(self.content_en.split())
        self.read_time = max(1, word_count // 200)
        
        super().save(*args, **kwargs)

    @property
    def is_published(self):
        """Check if post is published"""
        return self.status == 'published' and (
            self.published_at is None or 
            self.published_at <= timezone.now()
        )

    @property
    def get_absolute_url(self):
        """Get absolute URL for the post"""
        return f"/blog/{self.slug}/"

    def increment_views(self):
        """Increment view count"""
        self.views += 1
        self.save(update_fields=['views'])


class DesignCategory(models.Model):
    """
    Design categories for AI-generated designs
    """
    name_ar = models.CharField(max_length=255)
    name_en = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, null=True)
    
    # Visual
    image = models.CharField(max_length=500, blank=True, null=True)
    color_scheme = models.JSONField(
        default=list,
        help_text="Color palette for this category"
    )
    
    # Settings
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)
    
    # AI generation settings
    default_prompt_suffix = models.TextField(
        blank=True, null=True,
        help_text="Default AI prompt suffix for this category"
    )
    style_keywords = models.JSONField(
        default=list,
        help_text="Keywords for AI style generation"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['sort_order']),
        ]
        ordering = ['sort_order', 'name_ar']

    def __str__(self):
        return self.name_ar

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_en)
        super().save(*args, **kwargs)


class Design(models.Model):
    """
    AI-generated designs with metadata
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('archived', 'Archived'),
    ]
    
    # Basic information
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    # Visual assets
    image = models.CharField(max_length=500, blank=True, null=True)
    thumbnail = models.CharField(max_length=500, blank=True, null=True)
    high_res_image = models.CharField(max_length=500, blank=True, null=True)
    
    # Categorization
    category = models.ForeignKey(
        DesignCategory, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='designs'
    )
    tags = models.JSONField(default=list, blank=True)
    style_keywords = models.JSONField(default=list, blank=True)
    
    # User and attribution
    user = models.ForeignKey(
        'api_user.User', 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='designs'
    )
    is_anonymous = models.BooleanField(default=False)
    
    # Status and visibility
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Engagement metrics
    likes = models.IntegerField(default=0)
    downloads = models.IntegerField(default=0)
    views = models.IntegerField(default=0)
    shares = models.IntegerField(default=0)
    rating_average = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    rating_count = models.IntegerField(default=0)
    
    # AI generation metadata
    prompt = models.TextField(blank=True, null=True)
    ai_model = models.CharField(max_length=100, blank=True, null=True)
    generation_parameters = models.JSONField(default=dict, blank=True)
    generation_time = models.FloatField(blank=True, null=True)
    generated_at = models.DateTimeField(blank=True, null=True)
    
    # Technical specifications
    file_size = models.IntegerField(blank=True, null=True)
    resolution = models.CharField(max_length=50, blank=True, null=True)
    file_format = models.CharField(max_length=10, default='PNG')
    color_mode = models.CharField(max_length=20, blank=True, null=True)
    
    # Licensing and usage
    license_type = models.CharField(
        max_length=50,
        choices=[
            ('free', 'Free'),
            ('premium', 'Premium'),
            ('exclusive', 'Exclusive'),
        ],
        default='free'
    )
    commercial_use = models.BooleanField(default=True)
    attribution_required = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['user']),
            models.Index(fields=['status']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['is_active']),
            models.Index(fields=['is_public']),
            models.Index(fields=['generated_at']),
            models.Index(fields=['likes']),
            models.Index(fields=['downloads']),
            models.Index(fields=['rating_average']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def is_approved(self):
        """Check if design is approved"""
        return self.status == 'approved'

    @property
    def can_download(self):
        """Check if design can be downloaded"""
        return self.is_approved and self.is_active and self.is_public

    def increment_downloads(self):
        """Increment download count"""
        self.downloads += 1
        self.save(update_fields=['downloads'])

    def increment_likes(self):
        """Increment like count"""
        self.likes += 1
        self.save(update_fields=['likes'])

    def update_rating(self, new_rating):
        """Update average rating"""
        if self.rating_count == 0:
            self.rating_average = new_rating
        else:
            total_rating = self.rating_average * self.rating_count + new_rating
            self.rating_count += 1
            self.rating_average = total_rating / self.rating_count
        self.save(update_fields=['rating_average', 'rating_count'])
