"""Exercise native fragment links after focus-induced layout has settled."""
import re
from playwright.sync_api import expect


def follow_fragment(page, link, fragment):
    # locator.press() focuses and dispatches Enter in one browser task. Across
    # long pages that can race the browser's pending focus scroll. Establish
    # focus, allow rendering, then send a separate ordinary keyboard action.
    # Do not scroll the destination or assign location: the link must do that.
    link.focus()
    expect(link).to_be_focused()
    page.evaluate('()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))')
    page.keyboard.press('Enter')
    target = page.locator(fragment)
    try:
        expect(page).to_have_url(re.compile(re.escape(fragment) + '$'))
        expect(target).to_be_in_viewport()
    except AssertionError:
        print('Native fragment diagnostics:', page.evaluate('''selector=>{
            const target=document.querySelector(selector), active=document.activeElement;
            return {url:location.href,width:innerWidth,scrollY,active:active?.outerHTML,
                    target:target?.getBoundingClientRect().toJSON()};
        }''', fragment), flush=True)
        raise
