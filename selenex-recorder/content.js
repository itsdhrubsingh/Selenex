
const MAX_TEXT_LENGTH = 5000;

function sendAction(payload) {
    chrome.runtime.sendMessage({
        type: "USER_ACTION",
        payload
    });
}

/**
 * Capture stable, semantic context for an element
 */
function getElementContext(el) {
    const parents = [];
    let current = el.parentElement;
    let depth = 0;

    while (current && depth < 5) {
        parents.push({
            tag: current.tagName,
            id: current.id || null,
            class: current.className || null
        });
        current = current.parentElement;
        depth++;
    }

    return {
        tag: el.tagName,
        text: el.innerText?.trim(),
        attributes: {
            id: el.id,
            class: el.className,
            href: el.getAttribute("href"),
            name: el.getAttribute("name"),
            placeholder: el.getAttribute("placeholder"),
            role: el.getAttribute("role"),
            ariaExpanded: el.getAttribute("aria-expanded"),
            target: el.getAttribute("target"),
            type: el.getAttribute("type"),
            dataTestId: el.getAttribute("data-testid") || el.getAttribute("data-cy")
        },
        parentChain: parents
    };
}

/**
 * Generate a lightweight structural fingerprint of the page
 */
function getStructuralFingerprint() {
    // Simple hash of visible text (approximation)
    const text = document.body.innerText.slice(0, MAX_TEXT_LENGTH);
    let hash = 0;
    for (let i = 0; i < text.length; i++) {
        const char = text.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash; // Convert to 32bit integer
    }

    // Key structural elements
    const signature = Array.from(document.querySelectorAll("header, nav, main, footer, section, article"))
        .map(el => el.tagName.toLowerCase() + (el.id ? `#${el.id}` : ""));

    return {
        url: window.location.href,
        title: document.title,
        visibleTextHash: hash.toString(16),
        domSignature: signature.slice(0, 10) // Top 10 structural elements
    };
}

/* CLICK RECORD */
document.addEventListener("click", (e) => {
    // 1. Find closest interactive element
    let el = e.target.closest("a, button, input, textarea, select, [role='button']");

    // 2. Promotion Rule: Valid semantic parent (Anchor) trumps Button/Input
    if (el) {
        const semanticParent = el.closest("a[href]");
        if (semanticParent) {
            el = semanticParent;
        }
    }

    // 3. Fallback: Check for data-testid on the clicked element if nothing else found
    if (!el && e.target.hasAttribute("data-testid")) {
        el = e.target;
    }

    if (!el) return;

    const payload = {
        action: "click",
        elementContext: getElementContext(el),
        fingerprint: getStructuralFingerprint(),
        timestamp: Date.now()
    };

    sendAction(payload);
}, true);


/* SCROLL RECORD (Throttled) */
let scrollTimeout;
document.addEventListener("scroll", (e) => {
    if (scrollTimeout) return;

    scrollTimeout = setTimeout(() => {
        sendAction({
            action: "scroll",
            x: window.scrollX,
            y: window.scrollY,
            fingerprint: { url: location.href }, // Minimal fingerprint for scroll
            timestamp: Date.now()
        });
        scrollTimeout = null;
    }, 500);
}, true);

/* INPUT RECORD (Smart 'change' only) */
document.addEventListener("change", (e) => {
    const tag = e.target.tagName;
    if (!["INPUT", "TEXTAREA", "SELECT"].includes(tag)) return;

    // For inputs, we might want the value as well, which elementContext doesn't capture by default to avoid PII in generic contexts
    // But for a recorder, we often need it. Let's add it specifically for input events.
    const context = getElementContext(e.target);

    sendAction({
        action: "input",
        elementContext: context,
        value: e.target.value, // Capture value explicitly for inputs
        fingerprint: getStructuralFingerprint(),
        timestamp: Date.now()
    });
}, true);

/* KEYDOWN RECORD (Special keys) */
document.addEventListener("keydown", (e) => {
    if (!["Enter", "Escape", "Tab"].includes(e.key)) return;

    sendAction({
        action: "keydown",
        key: e.key,
        elementContext: getElementContext(e.target), // Context of focused element
        fingerprint: getStructuralFingerprint(),
        timestamp: Date.now()
    });
}, true);
