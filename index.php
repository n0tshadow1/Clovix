<!DOCTYPE html>
<html lang="en" data-bs-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YTdown - Download from YouTube, Instagram, Facebook</title>
    
    <!-- Bootstrap CSS with Replit Dark Theme -->
    <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
    
    <!-- Font Awesome Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <!-- Custom CSS -->
    <link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="index.php">
                <i class="fas fa-download me-2"></i>
                YTdown
            </a>
        </div>
    </nav>

    <main class="container my-4">
        <div class="row justify-content-center">
            <div class="col-lg-10">
                <!-- Platform Selection Tabs -->
                <div class="card mb-4">
                    <div class="card-header">
                        <h2 class="card-title mb-3">
                            <i class="fas fa-download me-2"></i>
                            YTdown
                        </h2>
                        <ul class="nav nav-tabs card-header-tabs" id="platform-tabs" role="tablist">
                            <li class="nav-item" role="presentation">
                                <button class="nav-link active" id="youtube-tab" data-bs-toggle="tab" data-bs-target="#youtube-pane" type="button" role="tab">
                                    <i class="fab fa-youtube text-danger me-2"></i>YouTube
                                </button>
                            </li>
                            <li class="nav-item" role="presentation">
                                <button class="nav-link" id="instagram-tab" data-bs-toggle="tab" data-bs-target="#instagram-pane" type="button" role="tab">
                                    <i class="fab fa-instagram text-primary me-2"></i>Instagram
                                </button>
                            </li>
                            <li class="nav-item" role="presentation">
                                <button class="nav-link" id="facebook-tab" data-bs-toggle="tab" data-bs-target="#facebook-pane" type="button" role="tab">
                                    <i class="fab fa-facebook text-info me-2"></i>Facebook
                                </button>
                            </li>
                            <li class="nav-item" role="presentation">
                                <button class="nav-link" id="twitter-tab" data-bs-toggle="tab" data-bs-target="#twitter-pane" type="button" role="tab">
                                    <i class="fab fa-twitter text-info me-2"></i>Twitter
                                </button>
                            </li>
                            <li class="nav-item" role="presentation">
                                <button class="nav-link" id="tiktok-tab" data-bs-toggle="tab" data-bs-target="#tiktok-pane" type="button" role="tab">
                                    <i class="fab fa-tiktok me-2"></i>TikTok
                                </button>
                            </li>
                            <li class="nav-item" role="presentation">
                                <button class="nav-link" id="other-tab" data-bs-toggle="tab" data-bs-target="#other-pane" type="button" role="tab">
                                    <i class="fas fa-globe me-2"></i>Other
                                </button>
                            </li>
                        </ul>
                    </div>
                    <div class="card-body">
                        <div class="tab-content" id="platform-tab-content">
                            <!-- YouTube Tab -->
                            <div class="tab-pane fade show active" id="youtube-pane" role="tabpanel">
                                <div class="platform-section">
                                    <div class="d-flex align-items-center mb-3">
                                        <i class="fab fa-youtube fa-2x text-danger me-3"></i>
                                        <div>
                                            <h5 class="mb-0">YouTube</h5>
                                            <p class="text-muted mb-0">Download videos, shorts, and music from YouTube</p>
                                        </div>
                                    </div>
                                    <form class="url-form" data-platform="youtube">
                                        <div class="input-group">
                                            <span class="input-group-text">
                                                <i class="fas fa-link"></i>
                                            </span>
                                            <input type="url" class="form-control video-url" 
                                                   placeholder="Paste YouTube URL here (e.g., https://youtube.com/watch?v=...)">
                                            <button class="btn btn-danger analyze-btn" type="submit">
                                                <i class="fas fa-search me-2"></i>Analyze
                                            </button>
                                        </div>
                                    </form>
                                </div>
                            </div>

                            <!-- Instagram Tab -->
                            <div class="tab-pane fade" id="instagram-pane" role="tabpanel">
                                <div class="platform-section">
                                    <div class="d-flex align-items-center mb-3">
                                        <i class="fab fa-instagram fa-2x text-primary me-3"></i>
                                        <div>
                                            <h5 class="mb-0">Instagram</h5>
                                            <p class="text-muted mb-0">Download posts, reels, stories, and IGTV videos</p>
                                        </div>
                                    </div>
                                    <form class="url-form" data-platform="instagram">
                                        <div class="input-group">
                                            <span class="input-group-text">
                                                <i class="fas fa-link"></i>
                                            </span>
                                            <input type="url" class="form-control video-url" 
                                                   placeholder="Paste Instagram URL here (e.g., https://instagram.com/p/...)">
                                            <button class="btn btn-primary analyze-btn" type="submit">
                                                <i class="fas fa-search me-2"></i>Analyze
                                            </button>
                                        </div>
                                    </form>
                                </div>
                            </div>

                            <!-- Facebook Tab -->
                            <div class="tab-pane fade" id="facebook-pane" role="tabpanel">
                                <div class="platform-section">
                                    <div class="d-flex align-items-center mb-3">
                                        <i class="fab fa-facebook fa-2x text-info me-3"></i>
                                        <div>
                                            <h5 class="mb-0">Facebook</h5>
                                            <p class="text-muted mb-0">Download videos from Facebook posts and pages</p>
                                        </div>
                                    </div>
                                    <form class="url-form" data-platform="facebook">
                                        <div class="input-group">
                                            <span class="input-group-text">
                                                <i class="fas fa-link"></i>
                                            </span>
                                            <input type="url" class="form-control video-url" 
                                                   placeholder="Paste Facebook URL here (e.g., https://facebook.com/...)">
                                            <button class="btn btn-info analyze-btn" type="submit">
                                                <i class="fas fa-search me-2"></i>Analyze
                                            </button>
                                        </div>
                                    </form>
                                </div>
                            </div>

                            <!-- Twitter Tab -->
                            <div class="tab-pane fade" id="twitter-pane" role="tabpanel">
                                <div class="platform-section">
                                    <div class="d-flex align-items-center mb-3">
                                        <i class="fab fa-twitter fa-2x text-info me-3"></i>
                                        <div>
                                            <h5 class="mb-0">Twitter / X</h5>
                                            <p class="text-muted mb-0">Download videos and GIFs from Twitter posts</p>
                                        </div>
                                    </div>
                                    <form class="url-form" data-platform="twitter">
                                        <div class="input-group">
                                            <span class="input-group-text">
                                                <i class="fas fa-link"></i>
                                            </span>
                                            <input type="url" class="form-control video-url" 
                                                   placeholder="Paste Twitter URL here (e.g., https://twitter.com/...)">
                                            <button class="btn btn-info analyze-btn" type="submit">
                                                <i class="fas fa-search me-2"></i>Analyze
                                            </button>
                                        </div>
                                    </form>
                                </div>
                            </div>

                            <!-- TikTok Tab -->
                            <div class="tab-pane fade" id="tiktok-pane" role="tabpanel">
                                <div class="platform-section">
                                    <div class="d-flex align-items-center mb-3">
                                        <i class="fab fa-tiktok fa-2x me-3"></i>
                                        <div>
                                            <h5 class="mb-0">TikTok</h5>
                                            <p class="text-muted mb-0">Download TikTok videos without watermark</p>
                                        </div>
                                    </div>
                                    <form class="url-form" data-platform="tiktok">
                                        <div class="input-group">
                                            <span class="input-group-text">
                                                <i class="fas fa-link"></i>
                                            </span>
                                            <input type="url" class="form-control video-url" 
                                                   placeholder="Paste TikTok URL here (e.g., https://tiktok.com/@...)">
                                            <button class="btn btn-dark analyze-btn" type="submit">
                                                <i class="fas fa-search me-2"></i>Analyze
                                            </button>
                                        </div>
                                    </form>
                                </div>
                            </div>

                            <!-- Other Platforms Tab -->
                            <div class="tab-pane fade" id="other-pane" role="tabpanel">
                                <div class="platform-section">
                                    <div class="d-flex align-items-center mb-3">
                                        <i class="fas fa-globe fa-2x text-secondary me-3"></i>
                                        <div>
                                            <h5 class="mb-0">Other Platforms</h5>
                                            <p class="text-muted mb-0">Vimeo, Dailymotion, and 1000+ other supported sites</p>
                                        </div>
                                    </div>
                                    <form class="url-form" data-platform="other">
                                        <div class="input-group">
                                            <span class="input-group-text">
                                                <i class="fas fa-link"></i>
                                            </span>
                                            <input type="url" class="form-control video-url" 
                                                   placeholder="Paste video URL from any supported platform...">
                                            <button class="btn btn-secondary analyze-btn" type="submit">
                                                <i class="fas fa-search me-2"></i>Analyze
                                            </button>
                                        </div>
                                    </form>
                                </div>
                            </div>
                        </div>

                        <!-- Loading Indicator -->
                        <div id="loading" class="text-center py-4" style="display: none;">
                            <div class="spinner-border text-primary pulse" role="status">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                            <p class="mt-2" style="color: rgba(255, 255, 255, 0.7);">Analyzing video...</p>
                        </div>

                        <!-- Error Display -->
                        <div id="error-display" class="alert alert-danger" style="display: none;" role="alert">
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            <span id="error-message"></span>
                        </div>

                        <!-- Download Options -->
                        <div id="download-options" style="display: none;">
                            <div class="download-options">
                                <h5 style="color: white; margin-bottom: 1.5rem;">
                                    <i class="fas fa-cog me-2"></i>
                                    Download Options
                                </h5>
                                
                                <!-- Format Selection -->
                                <div class="mb-4">
                                    <h6 style="color: rgba(255, 255, 255, 0.9); margin-bottom: 1rem;">Choose Format</h6>
                                    <div class="format-grid">
                                        <div class="format-option" data-format="video">
                                            <h6><i class="fas fa-video me-2"></i>Video</h6>
                                            <p>Download video with audio</p>
                                        </div>
                                        <div class="format-option" data-format="audio">
                                            <h6><i class="fas fa-music me-2"></i>Audio Only</h6>
                                            <p>Extract audio as MP3</p>
                                        </div>
                                    </div>
                                </div>

                                <!-- Quality Selection -->
                                <div id="quality-section" style="display: none;">
                                    <div class="quality-selector">
                                        <h6 style="color: rgba(255, 255, 255, 0.9);">
                                            <i class="fas fa-sliders-h me-2"></i>
                                            Select Quality
                                        </h6>
                                        <div class="quality-grid" id="quality-options">
                                            <!-- Quality options will be populated here -->
                                        </div>
                                    </div>
                                </div>

                                <!-- File Format Selection -->
                                <div id="file-format-section" style="display: none;">
                                    <div class="quality-selector">
                                        <h6 style="color: rgba(255, 255, 255, 0.9);">
                                            <i class="fas fa-file me-2"></i>
                                            File Format
                                        </h6>
                                        <div class="quality-grid" id="file-format-options">
                                            <!-- File format options will be populated here -->
                                        </div>
                                    </div>
                                </div>

                                <!-- Download Button -->
                                <div class="text-center mt-4">
                                    <button class="btn btn-success btn-lg" id="download-btn" disabled>
                                        <i class="fas fa-download me-2"></i>
                                        Download Now
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Features Card -->
                <div class="card">
                    <div class="card-header">
                        <h5 class="card-title mb-0">
                            <i class="fas fa-star me-2"></i>
                            Features & Capabilities
                        </h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <div class="feature-item mb-3">
                                    <i class="fas fa-video text-success me-3"></i>
                                    <div>
                                        <h6 style="color: white; margin-bottom: 0.5rem;">Multiple Video Formats</h6>
                                        <p style="color: rgba(255, 255, 255, 0.7); margin: 0; font-size: 0.9rem;">
                                            MP4, WebM, 3GP, AVI, MKV and more
                                        </p>
                                    </div>
                                </div>
                                <div class="feature-item mb-3">
                                    <i class="fas fa-music text-info me-3"></i>
                                    <div>
                                        <h6 style="color: white; margin-bottom: 0.5rem;">Audio Extraction</h6>
                                        <p style="color: rgba(255, 255, 255, 0.7); margin: 0; font-size: 0.9rem;">
                                            MP3, M4A, OGG, WAV formats
                                        </p>
                                    </div>
                                </div>
                                <div class="feature-item mb-3">
                                    <i class="fas fa-expand-arrows-alt text-warning me-3"></i>
                                    <div>
                                        <h6 style="color: white; margin-bottom: 0.5rem;">All Resolutions</h6>
                                        <p style="color: rgba(255, 255, 255, 0.7); margin: 0; font-size: 0.9rem;">
                                            144p to 4K (2160p) and beyond
                                        </p>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="feature-item mb-3">
                                    <i class="fas fa-bolt text-primary me-3"></i>
                                    <div>
                                        <h6 style="color: white; margin-bottom: 0.5rem;">Fast Downloads</h6>
                                        <p style="color: rgba(255, 255, 255, 0.7); margin: 0; font-size: 0.9rem;">
                                            Optimized for maximum speed
                                        </p>
                                    </div>
                                </div>
                                <div class="feature-item mb-3">
                                    <i class="fas fa-mobile-alt text-danger me-3"></i>
                                    <div>
                                        <h6 style="color: white; margin-bottom: 0.5rem;">Mobile Friendly</h6>
                                        <p style="color: rgba(255, 255, 255, 0.7); margin: 0; font-size: 0.9rem;">
                                            Works perfectly on all devices
                                        </p>
                                    </div>
                                </div>
                                <div class="feature-item mb-3">
                                    <i class="fas fa-shield-alt text-secondary me-3"></i>
                                    <div>
                                        <h6 style="color: white; margin-bottom: 0.5rem;">Safe & Secure</h6>
                                        <p style="color: rgba(255, 255, 255, 0.7); margin: 0; font-size: 0.9rem;">
                                            No registration or personal data required
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </main>

    <footer class="bg-dark text-center py-3 mt-5">
        <div class="container">
            <p class="mb-0 text-muted">
                <i class="fas fa-video me-2"></i>
                YTdown - Download from YouTube, Instagram, Facebook & More
            </p>
        </div>
    </footer>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    
    <!-- Custom JS -->
    <script src="assets/js/main.js"></script>
</body>
</html>