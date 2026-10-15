"""Exercise native fragment links after focus-induced layout has settled."""
import re
from playwright.sync_api import expect


def follow_fragment(page, link, fragment):
    # locator.press() focuses and dispatches Enter in one browser task. Across
    # long pages that can race the browser's pending focus scroll. Establish
    # focus, allow rendering, then send a separate ordinary keyboard action.
    # Do not scroll the destination or assign location: the link must do that.
    page.evaluate('()=>document.fonts.ready.then(()=>true)')
    link.focus()
    expect(link).to_be_focused()
    expect(link).to_be_in_viewport(ratio=1)
    # Native focus can schedule scrolling after the first rendering frame.
    # Wait for the focused link to settle before activating it. This does not
    # move the destination, change the URL or weaken the arrival assertions.
    link.evaluate('''async link=>{
        let previous=link.getBoundingClientRect().top, stable=0;
        for(let frame=0;frame<120;frame++){
            await new Promise(resolve=>requestAnimationFrame(resolve));
            const current=link.getBoundingClientRect().top;
            stable=Math.abs(current-previous)<0.5?stable+1:0;
            previous=current;
            if(stable>=6)return;
        }
        throw new Error('Focused fragment link did not settle');
    }''')
    expect(link).to_be_focused()
    page.keyboard.press('Enter')
    target = page.locator(fragment)
    try:
        expect(page).to_have_url(re.compile(re.escape(fragment) + '$'))
        expect(target).to_be_in_viewport()
    except AssertionError:
        print('Native fragment diagnostics:', page.evaluate('''selector=>{
            const target=document.querySelector(selector), active=document.activeElement;
            return {url:location.href,width:innerWidth,scrollY,active:active?.outerHTML.slice(0,500),
                    target:target?.getBoundingClientRect().toJSON()};
        }''', fragment), flush=True)
        raise
