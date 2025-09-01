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
  const browser = await puppeteer.launch({ headless: HEADLESS });
  const page = await browser.newPage();

  // Load cookies for authenticated session if available
  const cookiesPath = 'reddit_cookies.json';
  if (fs.existsSync(cookiesPath)) {
    const cookies = JSON.parse(fs.readFileSync(cookiesPath, 'utf8'));
    await page.setCookie(...cookies);
    console.log('Loaded cookies for authenticated session.');
  }

  let trackedEvents = [];
  let screenshotCount = 0;

  // Create output folder for this session
  const outDir = path.join('.', `session_${sessionId}`);
  if (!fs.existsSync(outDir)) {
    fs.mkdirSync(outDir);
  }

  // Set a realistic user-agent and accept-language
  await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36');
  await page.setExtraHTTPHeaders({ 'Accept-Language': 'en-US,en;q=0.9' });

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
  await page.goto(url, { waitUntil: 'networkidle2' });
  await page.waitForTimeout(randomDelay(2000, 4000)); // Initial wait

  // Simulate human-like actions before scrolling/screenshots
  try {
    // Move mouse and click somewhere harmless
    await page.mouse.move(200, 200);
    await page.mouse.click(200, 200);
    // Type in the search box if present
    await page.evaluate(() => {
      const search = document.querySelector('input[type="search"]');
      if (search) {
        search.focus();
        search.value = 'test';
        search.dispatchEvent(new Event('input', { bubbles: true }));
      }
    });
    // Scroll a bit up and down
    await page.evaluate(() => window.scrollBy(0, 300));
    await page.waitForTimeout(1000);
    await page.evaluate(() => window.scrollBy(0, -150));
    await page.waitForTimeout(1000);
  } catch (e) {}

  // Inject global CSS to hide banners/modals for the whole session
  await page.addStyleTag({content: `
    [data-testid="bottom-bar"],
    .XPromoPopup__closeButton,
    [aria-label="Close"],
    .XPromoPopup,
    .XPromoPill,
    .XPromoPill__container,
    .XPromoPill__content,
    .XPromoPill__close {
      display: none !important;
      visibility: hidden !important;
      opacity: 0 !important;
      pointer-events: none !important;
    }
  `});

  // Try to close the Reddit login/signup banner/modal and bottom bar if present (initial)
  try {
    await page.evaluate(() => {
      const closeBtn = document.querySelector('button[aria-label="Close"], .XPromoPopup__closeButton');
      if (closeBtn) closeBtn.click();
      const loginBar = document.querySelector('div[data-testid="bottom-bar"]');
      if (loginBar) loginBar.style.display = 'none';
      const topBar = document.querySelector('header[role="banner"]');
      if (topBar && topBar.style.position === 'fixed') topBar.style.display = 'none';
    });
    await page.waitForTimeout(1000); // Let UI update
  } catch (e) {}

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
        const closeBtn = document.querySelector('button[aria-label="Close"], .XPromoPopup__closeButton');
        if (closeBtn) closeBtn.click();
        const loginBar = document.querySelector('div[data-testid="bottom-bar"]');
        if (loginBar) loginBar.style.display = 'none';
      });
    } catch (e) {}

    // Simulate user actions for this viewport
    for (let j = 0; j < EVENTS_PER_VIEWPORT; j++) {
      // Try to click a button or menuitem (less likely to navigate)
      const didClick = await page.evaluate(() => {
        const elements = Array.from(document.querySelectorAll('button, [role=button], [role=menuitem], input[type=button], input[type=submit]'))
          .filter(el => el.offsetParent !== null);
        if (elements.length > 0) {
          const el = elements[Math.floor(Math.random() * elements.length)];
          el.scrollIntoView({ behavior: 'smooth', block: 'center' });
          el.click();
          return true;
        }
        return false;
      });
      // If no button/menuitem was clicked, try to click a link (may navigate)
      if (!didClick) {
        const didNav = await page.evaluate(() => {
          const links = Array.from(document.querySelectorAll('a'))
            .filter(el => el.offsetParent !== null && el.href && !el.href.startsWith('javascript:'));
          if (links.length > 0) {
            const el = links[Math.floor(Math.random() * links.length)];
            el.scrollIntoView({ behavior: 'smooth', block: 'center' });
            el.click();
            return true;
          }
          return false;
        });
        if (didNav) {
          try {
            await page.waitForNavigation({ timeout: 5000, waitUntil: 'networkidle2' });
          } catch (e) {
            // Navigation may not always happen, ignore timeout
          }
        }
      }
      // Random scroll within viewport
      await page.evaluate(() => window.scrollBy(0, Math.random() * 200));
      // Random input (if any)
      await page.evaluate(() => {
        const input = document.querySelector('input[type="text"]');
        if (input) {
          input.focus();
          input.value = 'test';
          input.dispatchEvent(new Event('input', { bubbles: true }));
        }
      });
      await page.waitForTimeout(randomDelay()); // Human-like delay
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