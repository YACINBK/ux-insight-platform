#!/usr/bin/env node

/**
 * Premium Auto Mode Automation Script
 * Enhanced with successful techniques from smart_viewport_tracker.cjs
 * 
 * Usage: node automation_script.cjs <url> [analysis_id]
 * Example: node automation_script.cjs https://www.reddit.com/r/technology
 */

// Use puppeteer-extra and stealth plugin for bot evasion
const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
puppeteer.use(StealthPlugin());

const fs = require('fs').promises;
const path = require('path');
const axios = require('axios');

function randomDelay(min = 1000, max = 2500) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

class WebsiteAnalyzer {
    constructor() {
        this.browser = null;
        this.page = null;
        this.results = {
            url: '',
            timestamp: new Date().toISOString(),
            screenshots: [],
            metrics: {},
            recommendations: [],
            analysis_id: '',
            tracked_events: []
        };
        this.backendUrl = 'http://localhost:8080';
        this.resultsPath = path.join(__dirname, 'analysis_results.json');
        this.isFirstWrite = true;
    }

    // New method for incremental JSON saving
    async saveIncrementalResults() {
        try {
            const dataToSave = {
                ...this.results,
                last_updated: new Date().toISOString(),
                progress: {
                    screenshots_count: this.results.screenshots.length,
                    events_count: this.results.tracked_events.length,
                    is_complete: false
                }
            };

            // Use atomic write to prevent corruption
            const tempPath = this.resultsPath + '.tmp';
            await fs.writeFile(tempPath, JSON.stringify(dataToSave, null, 2));
            await fs.rename(tempPath, this.resultsPath);

            if (this.isFirstWrite) {
                console.log(`💾 Initial results saved to: ${this.resultsPath}`);
                this.isFirstWrite = false;
            } else {
                console.log(`💾 Incremental update saved (${this.results.screenshots.length} screenshots, ${this.results.tracked_events.length} events)`);
            }
        } catch (error) {
            console.error('⚠️ Error saving incremental results:', error.message);
        }
    }

    async initialize() {
        console.log('🚀 Initializing browser with stealth mode...');
        this.browser = await puppeteer.launch({
            headless: true,
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu'
            ]
        });
        this.page = await this.browser.newPage();
        
        // Set realistic viewport and user agent
        await this.page.setViewport({ width: 1200, height: 800 });
        await this.page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36');
        await this.page.setExtraHTTPHeaders({ 'Accept-Language': 'en-US,en;q=0.9' });

        // Load cookies for authenticated session if available
        const cookiesPath = 'reddit_cookies.json';
        try {
            const cookiesData = await fs.readFile(cookiesPath, 'utf8');
            const cookies = JSON.parse(cookiesData);
            await this.page.setCookie(...cookies);
            console.log('✅ Loaded cookies for authenticated session.');
        } catch (e) {
            console.log('⚠️ No cookies file found. Will work around banners.');
        }

        // Expose function to record events
        await this.page.exposeFunction('recordEvent', async event => {
            this.results.tracked_events.push(event);
            // Save incremental results after each event (but limit frequency to avoid too many writes)
            if (this.results.tracked_events.length % 5 === 0) { // Save every 5 events
                await this.saveIncrementalResults();
            }
        });

        // Inject tracking script
        await this.page.evaluateOnNewDocument(() => {
            window.addEventListener('click', e => {
                const el = e.target;
                const rect = el.getBoundingClientRect();
                window.recordEvent({
                    timestamp: new Date().toISOString(),
                    eventType: 'click',
                    elementType: el.tagName.toLowerCase(),
                    elementText: el.innerText || el.value || '',
                    elementClasses: el.className,
                    bbox: {
                        x: rect.x,
                        y: rect.y,
                        width: rect.width,
                        height: rect.height
                    },
                    url: window.location.href
                });
            });

            window.addEventListener('scroll', e => {
                window.recordEvent({
                    timestamp: new Date().toISOString(),
                    eventType: 'scroll',
                    elementType: 'body',
                    elementText: '',
                    elementClasses: '',
                    bbox: null,
                    url: window.location.href
                });
            });
        });
        
        console.log('✅ Browser initialized successfully with tracking');
    }

    async removeBanners() {
        console.log('🛡️ Removing banners and modals...');
        
        // Multiple attempts to remove banners
        for (let attempt = 1; attempt <= 5; attempt++) {
            try {
                await this.page.evaluate(() => {
                    // Remove all possible banner elements
                    const selectors = [
                        '[data-testid="bottom-bar"]',
                        '[data-testid="login-signup-banner"]',
                        '[data-testid="login-signup-modal"]',
                        '.XPromoPopup__closeButton',
                        '[aria-label="Close"]',
                        '.XPromoPopup',
                        '.XPromoPill',
                        '.XPromoPill__container',
                        '.XPromoPill__content',
                        '.XPromoPill__close',
                        '.LoginSignupModal',
                        '.LoginSignupBanner',
                        '.BottomBar',
                        '.TopBar',
                        '.RedditHeader__login',
                        '.RedditHeader__signup',
                        'button[data-testid="login-button"]',
                        'button[data-testid="signup-button"]'
                    ];
                    
                    selectors.forEach(selector => {
                        const elements = document.querySelectorAll(selector);
                        elements.forEach(el => {
                            el.style.display = 'none';
                            el.style.visibility = 'hidden';
                            el.style.opacity = '0';
                            el.style.pointerEvents = 'none';
                            el.remove();
                        });
                    });
                    
                    // Click any close buttons
                    const closeButtons = document.querySelectorAll('button[aria-label="Close"], .XPromoPopup__closeButton, [data-testid="close-button"]');
                    closeButtons.forEach(btn => btn.click());
                });
                
                await this.page.waitForTimeout(1000);
                console.log(`✅ Banner removal attempt ${attempt} completed.`);
                
            } catch (e) {
                console.log(`⚠️ Banner removal attempt ${attempt} failed:`, e.message);
            }
        }

        // Inject global CSS to hide banners permanently
        await this.page.addStyleTag({content: `
            [data-testid="bottom-bar"],
            [data-testid="login-signup-banner"],
            [data-testid="login-signup-modal"],
            .XPromoPopup__closeButton,
            [aria-label="Close"],
            .XPromoPopup,
            .XPromoPill,
            .XPromoPill__container,
            .XPromoPill__content,
            .XPromoPill__close,
            .LoginSignupModal,
            .LoginSignupBanner,
            .BottomBar,
            .TopBar,
            .RedditHeader__login,
            .RedditHeader__signup,
            button[data-testid="login-button"],
            button[data-testid="signup-button"] {
                display: none !important;
                visibility: hidden !important;
                opacity: 0 !important;
                pointer-events: none !important;
                position: absolute !important;
                top: -9999px !important;
                left: -9999px !important;
            }
        `});
    }

    async simulateHumanBehavior() {
        console.log('🤖 Simulating human-like behavior...');
        
        try {
            // Move mouse and click somewhere harmless
            await this.page.mouse.move(200, 200);
            await this.page.mouse.click(200, 200);
            
            // Type in search box if present (avoid login fields)
            await this.page.evaluate(() => {
                const search = document.querySelector('input[type="search"], input[placeholder*="search"], input[placeholder*="Search"]');
                if (search && !search.name.includes('login') && !search.name.includes('password')) {
                    search.focus();
                    search.value = 'technology';
                    search.dispatchEvent(new Event('input', { bubbles: true }));
                }
            });
            
            // Scroll naturally
            await this.page.evaluate(() => window.scrollBy(0, 300));
            await this.page.waitForTimeout(randomDelay());
            await this.page.evaluate(() => window.scrollBy(0, -150));
            await this.page.waitForTimeout(randomDelay());
            
        } catch (e) {
            console.log('⚠️ Human simulation failed:', e.message);
        }
    }

    async analyzeWebsite(url, analysisId = null) {
        try {
            console.log(`🔍 Analyzing website: ${url}`);
            this.results.url = url;
            this.results.analysis_id = analysisId || this.generateAnalysisId();

            // Navigate to the website
            await this.page.goto(url, { 
                waitUntil: 'networkidle2',
                timeout: 30000 
            });
            
            // Wait for cookies to take effect
            await this.page.waitForTimeout(3000);
            
            console.log(`✅ Page loaded. Current URL: ${this.page.url()}`);

            // Remove banners and simulate human behavior
            await this.removeBanners();
            await this.simulateHumanBehavior();

            // Take screenshots
            await this.takeScreenshots();
            
            // Collect metrics
            await this.collectMetrics();
            
            // Generate recommendations
            await this.generateRecommendations();
            
            // Send results to backend
            await this.sendResultsToBackend();
            
            console.log('✅ Analysis completed successfully');
            return this.results;

        } catch (error) {
            console.error('❌ Error during analysis:', error.message);
            throw error;
        }
    }

    async takeScreenshots() {
        console.log('📸 Taking screenshots...');
        
        const screenshotDir = path.join(__dirname, 'screenshots');
        await fs.mkdir(screenshotDir, { recursive: true });
        
        // Get page dimensions
        const viewportHeight = await this.page.evaluate(() => window.innerHeight);
        const pageHeight = await this.page.evaluate(() => document.body.scrollHeight);
        const numScreens = Math.ceil(pageHeight / viewportHeight);
        
        console.log(`📏 Page height: ${pageHeight}, viewport: ${viewportHeight}, screens: ${numScreens}`);

        // Take viewport screenshots
        for (let i = 0; i < numScreens; i++) {
            // Scroll to position
            await this.page.evaluate(y => window.scrollTo(0, y), i * viewportHeight);
            await this.page.waitForTimeout(randomDelay(1200, 2000));
            
            // Remove banners again before screenshot
            await this.removeBanners();
            
            // Take screenshot
            const screenshotPath = path.join(screenshotDir, `viewport_${i}.png`);
            await this.page.screenshot({ path: screenshotPath });
            this.results.screenshots.push(screenshotPath);
            
            console.log(`✅ Screenshot ${i + 1}/${numScreens} saved: ${screenshotPath}`);
            
            // Save incremental results after each screenshot
            await this.saveIncrementalResults();
        }
        
        // Full page screenshot
        const fullPagePath = path.join(screenshotDir, 'fullpage.png');
        await this.page.screenshot({ 
            path: fullPagePath, 
            fullPage: true 
        });
        this.results.screenshots.push(fullPagePath);
        
        // Save incremental results after full page screenshot
        await this.saveIncrementalResults();
        
        console.log(`✅ Total screenshots saved: ${this.results.screenshots.length} files`);
    }

    async collectMetrics() {
        console.log('📊 Collecting metrics...');
        
        const metrics = await this.page.evaluate(() => {
            const elements = document.querySelectorAll('*');
            const images = document.querySelectorAll('img');
            const links = document.querySelectorAll('a');
            const buttons = document.querySelectorAll('button, input[type="button"], input[type="submit"]');
            const forms = document.querySelectorAll('form');
            const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
            
            // Check for viewport meta tag
            const viewportMeta = document.querySelector('meta[name="viewport"]');
            
            // Count images with alt text
            let altTextImages = 0;
            images.forEach(img => {
                if (img.alt && img.alt.trim() !== '') {
                    altTextImages++;
                }
            });
            
            return {
                totalElements: elements.length,
                images: images.length,
                links: links.length,
                buttons: buttons.length,
                forms: forms.length,
                headings: headings.length,
                altTextImages: altTextImages,
                totalImages: images.length,
                hasViewport: !!viewportMeta
            };
        });
        
        this.results.metrics = metrics;
        console.log('✅ Metrics collected:', metrics);
    }

    async generateRecommendations() {
        console.log('💡 Generating recommendations...');
        
        const metrics = this.results.metrics;
        const recommendations = [];
        
        // Accessibility recommendations
        if (metrics.images > 0 && metrics.altTextImages < metrics.images) {
            recommendations.push('Add alt text to images for better accessibility');
        }
        
        if (metrics.headings < 3) {
            recommendations.push('Consider adding more heading elements for better content structure');
        }
        
        // SEO recommendations
        if (!metrics.hasViewport) {
            recommendations.push('Add viewport meta tag for better mobile responsiveness');
        }
        
        // UX recommendations
        if (metrics.buttons < 2) {
            recommendations.push('Consider adding more call-to-action buttons');
        }
        
        if (metrics.forms > 0 && metrics.buttons < 1) {
            recommendations.push('Add submit buttons to forms for better user interaction');
        }
        
        // Performance recommendations
        if (metrics.images > 10) {
            recommendations.push('Consider optimizing images for faster loading');
        }
        
        this.results.recommendations = recommendations;
        console.log(`✅ Generated ${recommendations.length} recommendations`);
    }

    async sendResultsToBackend() {
        console.log('📤 Sending results to backend...');
        
        try {
            // Prepare the results payload
            const payload = {
                url: this.results.url,
                analysis_id: this.results.analysis_id,
                metrics: this.results.metrics,
                recommendations: this.results.recommendations,
                screenshots: this.results.screenshots,
                tracked_events: this.results.tracked_events,
                timestamp: this.results.timestamp
            };

            // Send to backend endpoint
            const response = await axios.post(`${this.backendUrl}/api/questions/premium-auto/automation-results`, payload, {
                headers: {
                    'Content-Type': 'application/json'
                },
                timeout: 30000
            });

            console.log('✅ Results sent to backend successfully');
            return response.data;

        } catch (error) {
            console.error('❌ Error sending results to backend:', error.message);
            // Don't throw error, just log it
        }
    }

    async saveResults() {
        // Mark analysis as complete
        this.results.progress = {
            screenshots_count: this.results.screenshots.length,
            events_count: this.results.tracked_events.length,
            is_complete: true,
            completed_at: new Date().toISOString()
        };

        // Save final results
        await fs.writeFile(this.resultsPath, JSON.stringify(this.results, null, 2));
        console.log(`💾 Final results saved to: ${this.resultsPath}`);
        console.log(`🎯 Analysis completed: ${this.results.screenshots.length} screenshots, ${this.results.tracked_events.length} events`);
    }

    generateAnalysisId() {
        return 'auto_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    async cleanup() {
        // Save current progress before cleanup
        if (this.results.screenshots.length > 0 || this.results.tracked_events.length > 0) {
            console.log('💾 Saving current progress before cleanup...');
            await this.saveIncrementalResults();
        }

        if (this.browser) {
            await this.browser.close();
            console.log('🧹 Browser closed');
        }
    }

    // Add graceful shutdown handling
    setupGracefulShutdown() {
        const shutdown = async (signal) => {
            console.log(`\n🛑 Received ${signal}. Saving current progress...`);
            await this.saveIncrementalResults();
            console.log('✅ Progress saved. Exiting gracefully.');
            process.exit(0);
        };

        process.on('SIGINT', () => shutdown('SIGINT'));
        process.on('SIGTERM', () => shutdown('SIGTERM'));
    }
}

// Main execution
async function main() {
    const url = process.argv[2];
    const analysisId = process.argv[3]; // Optional analysis ID from backend
    
    if (!url) {
        console.error('❌ Please provide a URL as an argument');
        console.log('Usage: node automation_script.cjs <url> [analysis_id]');
        process.exit(1);
    }
    
    const analyzer = new WebsiteAnalyzer();
    
    try {
        analyzer.setupGracefulShutdown(); // Set up graceful shutdown
        await analyzer.initialize();
        await analyzer.analyzeWebsite(url, analysisId);
        await analyzer.saveResults();
        console.log('🎉 Analysis completed successfully!');
    } catch (error) {
        console.error('💥 Analysis failed:', error.message);
        process.exit(1);
    } finally {
        await analyzer.cleanup();
    }
}

// Run if called directly
if (require.main === module) {
    main();
}

module.exports = WebsiteAnalyzer; 