// Use puppeteer-extra and stealth plugin for bot evasion
const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
puppeteer.use(StealthPlugin());
const fs = require('fs');
const { v4: uuidv4 } = require('uuid');
const path = require('path');

// CONFIGURATION
const TARGET_URL = 'https://www.reddit.com/r/webdev/'; // Use a subreddit
const EVENTS_PER_VIEWPORT = 6; // Number of simulated actions per viewport
const HEADLESS = true; // Set to false to watch the browser

function getElementType(el) {
  if (el.tagName === 'BUTTON') return 'button';
  if (el.tagName === 'A') return 'link';
  if (el.tagName === 'INPUT' && ['button', 'submit'].includes(el.type)) return 'button';
  if (el.getAttribute('role') === 'button') return 'button';
  if (el.getAttribute('role') === 'menuitem') return 'menuitem';
  if (el.className && el.className.toLowerCase().includes('btn')) return 'button';
  return el.tagName.toLowerCase();
}

function randomDelay(min = 1200, max = 3500) {
  // Human-like delay between actions (1.2s to 3.5s)
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

async function simulateSession(sessionId, url) {
  const browser = await puppeteer.launch({ 
    headless: HEADLESS,
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
  
  const page = await browser.newPage();

  // Set a realistic user-agent and accept-language BEFORE loading cookies
  await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36');
  await page.setExtraHTTPHeaders({ 'Accept-Language': 'en-US,en;q=0.9' });

  // Load cookies for authenticated session if available
  const cookiesPath = 'reddit_cookies.json';
  if (fs.existsSync(cookiesPath)) {
    try {
      const cookies = JSON.parse(fs.readFileSync(cookiesPath, 'utf8'));
      await page.setCookie(...cookies);
      console.log('✅ Loaded cookies for authenticated session.');
    } catch (e) {
      console.log('⚠️ Error loading cookies:', e.message);
    }
  } else {
    console.log('⚠️ No cookies file found. Will try to work around banners.');
  }

  let trackedEvents = [];
  let screenshotCount = 0;

  // Create output folder for this session
  const outDir = path.join('.', `session_${sessionId}`);
  if (!fs.existsSync(outDir)) {
    fs.mkdirSync(outDir);
  }

  // Expose a function to record events from the page context
  await page.exposeFunction('recordEvent', event => {
    trackedEvents.push(event);
  });

  // Inject tracking script
  await page.evaluateOnNewDocument(() => {
    window.addEventListener('click', e => {
      const el = e.target;
      const rect = el.getBoundingClientRect();
      window.recordEvent({
        sessionId: window.__sessionId,
        timestamp: new Date().toISOString(),
        eventType: 'click',
        elementType: (function(el) {
          if (el.tagName === 'BUTTON') return 'button';
          if (el.tagName === 'A') return 'link';
          if (el.tagName === 'INPUT' && ['button', 'submit'].includes(el.type)) return 'button';
          if (el.getAttribute('role') === 'button') return 'button';
          if (el.getAttribute('role') === 'menuitem') return 'menuitem';
          if (el.className && el.className.toLowerCase().includes('btn')) return 'button';
          return el.tagName.toLowerCase();
        })(el),
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
        sessionId: window.__sessionId,
        timestamp: new Date().toISOString(),
        eventType: 'scroll',
        elementType: 'body',
        elementText: '',
        elementClasses: '',
        bbox: null,
        url: window.location.href
      });
    });
    window.addEventListener('input', e => {
      const el = e.target;
      const rect = el.getBoundingClientRect();
      window.recordEvent({
        sessionId: window.__sessionId,
        timestamp: new Date().toISOString(),
        eventType: 'input',
        elementType: el.tagName.toLowerCase(),
        elementText: el.value || '',
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
  });

  // Set sessionId in page context
  await page.evaluateOnNewDocument(sessionId => {
    window.__sessionId = sessionId;
  }, sessionId);

  // Go to the target URL
  console.log(`[${sessionId}] Navigating to ${url} ...`);
  await page.goto(url, { waitUntil: 'networkidle2', timeout: 30000 });
  
  // Wait for cookies to take effect
  await page.waitForTimeout(3000);
  
  console.log(`[${sessionId}] Page loaded. Current URL: ${page.url()}`);

  // AGGRESSIVE BANNER REMOVAL - Multiple attempts
  console.log(`[${sessionId}] Attempting to remove banners...`);
  
  for (let attempt = 1; attempt <= 5; attempt++) {
    try {
      await page.evaluate(() => {
        // Remove all possible banner elements
        const selectors = [
          '[data-testid="bottom-bar"]',
          '.XPromoPopup__closeButton',
          '[aria-label="Close"]',
          '.XPromoPopup',
          '.XPromoPill',
          '.XPromoPill__container',
          '.XPromoPill__content',
          '.XPromoPill__close',
          'div[data-testid="login-signup-banner"]',
          'div[data-testid="login-signup-modal"]',
          '.LoginSignupModal',
          '.LoginSignupBanner',
          'button[data-testid="login-button"]',
          'button[data-testid="signup-button"]',
          '.BottomBar',
          '.TopBar',
          'header[role="banner"]',
          '.RedditHeader',
          '.RedditHeader__login',
          '.RedditHeader__signup'
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
        
        // Hide fixed position elements that might be banners
        const fixedElements = document.querySelectorAll('*');
        fixedElements.forEach(el => {
          const style = window.getComputedStyle(el);
          if (style.position === 'fixed' && (el.style.zIndex > 1000 || el.className.includes('banner') || el.className.includes('modal'))) {
            el.style.display = 'none';
          }
        });
      });
      
      await page.waitForTimeout(1000);
      console.log(`[${sessionId}] Banner removal attempt ${attempt} completed.`);
      
    } catch (e) {
      console.log(`[${sessionId}] Banner removal attempt ${attempt} failed:`, e.message);
    }
  }

  // Inject global CSS to hide banners/modals for the whole session
  await page.addStyleTag({content: `
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

  // Check if we're still on the login page
  const currentUrl = page.url();
  if (currentUrl.includes('login') || currentUrl.includes('signup') || currentUrl.includes('auth')) {
    console.log(`[${sessionId}] ⚠️ Still on login page. Trying to navigate to subreddit directly...`);
    await page.goto('https://www.reddit.com/r/webdev/', { waitUntil: 'networkidle2', timeout: 30000 });
    await page.waitForTimeout(3000);
  }

  // Simulate human-like actions before scrolling/screenshots
  try {
    console.log(`[${sessionId}] Simulating human-like actions...`);
    
    // Move mouse and click somewhere harmless
    await page.mouse.move(200, 200);
    await page.mouse.click(200, 200);
    
    // Type in the search box if present (avoid login fields)
    await page.evaluate(() => {
      const search = document.querySelector('input[type="search"], input[placeholder*="search"], input[placeholder*="Search"]');
      if (search && !search.name.includes('login') && !search.name.includes('password')) {
        search.focus();
        search.value = 'web development';
        search.dispatchEvent(new Event('input', { bubbles: true }));
      }
    });
    
    // Scroll a bit up and down
    await page.evaluate(() => window.scrollBy(0, 300));
    await page.waitForTimeout(1000);
    await page.evaluate(() => window.scrollBy(0, -150));
    await page.waitForTimeout(1000);
    
  } catch (e) {
    console.log(`[${sessionId}] Human simulation failed:`, e.message);
  }

  // Get page and viewport height
  const viewportHeight = await page.evaluate(() => window.innerHeight);
  const pageHeight = await page.evaluate(() => document.body.scrollHeight);
  const numScreens = Math.ceil(pageHeight / viewportHeight);
  console.log(`[${sessionId}] Page height: ${pageHeight}, viewport: ${viewportHeight}, screens: ${numScreens}`);

  for (let i = 0; i < numScreens; i++) {
    // Scroll to position
    await page.evaluate(y => window.scrollTo(0, y), i * viewportHeight);
    await page.waitForTimeout(randomDelay(1200, 2000)); // Let the page settle

    // Try to close/hide the banner again before each screenshot
    try {
      await page.evaluate(() => {
        // Remove any new banners that appeared
        const selectors = [
          '[data-testid="bottom-bar"]',
          '.XPromoPopup',
          '.LoginSignupModal',
          '.LoginSignupBanner'
        ];
        
        selectors.forEach(selector => {
          const elements = document.querySelectorAll(selector);
          elements.forEach(el => {
            el.style.display = 'none';
            el.remove();
          });
        });
        
        // Click close buttons
        const closeButtons = document.querySelectorAll('button[aria-label="Close"], .XPromoPopup__closeButton');
        closeButtons.forEach(btn => btn.click());
      });
    } catch (e) {}

    // Simulate user actions for this viewport (AVOID LOGIN ELEMENTS)
    for (let j = 0; j < EVENTS_PER_VIEWPORT; j++) {
      try {
        // Try to click safe elements only (avoid login/signup)
        const didClick = await page.evaluate(() => {
          const safeElements = Array.from(document.querySelectorAll('button, [role=button], [role=menuitem], input[type=button], input[type=submit], a'))
            .filter(el => {
              // Filter out login/signup related elements
              const text = (el.innerText || el.value || '').toLowerCase();
              const classes = (el.className || '').toLowerCase();
              const id = (el.id || '').toLowerCase();
              
              return el.offsetParent !== null && 
                     !text.includes('login') && 
                     !text.includes('sign up') && 
                     !text.includes('signup') && 
                     !text.includes('log in') &&
                     !classes.includes('login') &&
                     !classes.includes('signup') &&
                     !id.includes('login') &&
                     !id.includes('signup');
            });
          
          if (safeElements.length > 0) {
            const el = safeElements[Math.floor(Math.random() * safeElements.length)];
            el.scrollIntoView({ behavior: 'smooth', block: 'center' });
            el.click();
            return true;
          }
          return false;
        });
        
        // Random scroll within viewport
        await page.evaluate(() => window.scrollBy(0, Math.random() * 200));
        
        // Random input (avoid login fields)
        await page.evaluate(() => {
          const inputs = document.querySelectorAll('input[type="text"], input[type="search"]');
          const safeInputs = Array.from(inputs).filter(input => {
            const name = (input.name || '').toLowerCase();
            const placeholder = (input.placeholder || '').toLowerCase();
            return !name.includes('login') && 
                   !name.includes('password') && 
                   !name.includes('email') &&
                   !placeholder.includes('login') &&
                   !placeholder.includes('password') &&
                   !placeholder.includes('email');
          });
          
          if (safeInputs.length > 0) {
            const input = safeInputs[Math.floor(Math.random() * safeInputs.length)];
            input.focus();
            input.value = 'test';
            input.dispatchEvent(new Event('input', { bubbles: true }));
          }
        });
        
        await page.waitForTimeout(randomDelay()); // Human-like delay
        
      } catch (e) {
        console.log(`[${sessionId}] Action simulation failed:`, e.message);
      }
    }

    // Take screenshot (viewport only)
    const screenshotPath = path.join(outDir, `screenshot_${i}.png`);
    await page.screenshot({ path: screenshotPath });
    
    // Save tracked events for this viewport
    const trackedDataPath = path.join(outDir, `tracked_${i}.json`);
    fs.writeFileSync(trackedDataPath, JSON.stringify(trackedEvents, null, 2));
    console.log(`[${sessionId}] Saved ${screenshotPath} and ${trackedDataPath}`);
    trackedEvents = []; // Reset for next viewport
    screenshotCount++;
  }

  await browser.close();
  console.log(`[${sessionId}] Done! Saved ${screenshotCount} screenshots and tracked data files in ${outDir}.`);
}

(async () => {
  const sessionId = uuidv4();
  await simulateSession(sessionId, TARGET_URL);
})(); 