"""Regression checks for native link intent and result-heading visibility."""
import json
from playwright.sync_api import expect

TEXT_SPACING = '*{line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important}p{margin-bottom:2em!important}'


def check_navigation(page, root):
    total = len(json.loads((root / '_source/poker/resources.json').read_text())['entries'])
    motion = page.add_style_tag(content='html{scroll-behavior:auto!important}')
    page.locator('#resource-reset').click()
    search = page.locator('#resource-search')
    search.fill('ICM')
    expect(page.locator('#resource-omaha-rules')).to_be_hidden()
    # The test cancels default navigation only AFTER the application's handler.
    # Observe defaultPrevented first, so an app that cancels native behavior fails.
    results = page.evaluate("""async () => {
      const link=document.querySelector('#directory-top a[href="#resource-ncpg"]');
      const input=document.getElementById('resource-search');
      const snapshot=()=>JSON.stringify({
        input:input.value, count:document.getElementById('resource-count').textContent,
        format:document.getElementById('resource-format').value,
        level:document.getElementById('resource-level').value,
        free:document.getElementById('resource-free').getAttribute('aria-pressed'),
        topic:document.querySelector('[data-resource-filter][aria-pressed="true"]').dataset.resourceFilter,
        url:location.href, focus:document.activeElement.id, x:scrollX,y:scrollY
      });
      const frames=()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));
      input.focus({preventScroll:true}); await frames();
      const cases=[
        {ctrlKey:true},{metaKey:true},{shiftKey:true},{altKey:true},{button:1},{button:2},
        {alreadyPrevented:true}
      ], results=[];
      for (const options of cases) {
        document.getElementById('resource-reset').click();
        input.value='ICM';input.dispatchEvent(new Event('search'));
        input.focus({preventScroll:true});await frames();
        const before=snapshot();
        const event=new MouseEvent('click',{bubbles:true,cancelable:true,button:0,...options});
        if(options.alreadyPrevented) event.preventDefault();
        let observed=null;
        const stop=e=>{observed=e.defaultPrevented;e.preventDefault();};
        document.addEventListener('click',stop,{once:true});
        link.dispatchEvent(event); await frames();
        results.push({options, preserved:before===snapshot(), nativePreserved:observed===Boolean(options.alreadyPrevented)});
      }
      return results;
    }""")
    assert all(r['preserved'] and r['nativePreserved'] for r in results), results
    motion.evaluate('(node)=>node.remove()')
    # Ordinary mouse and keyboard activation still reveal and focus hidden targets.
    for keyboard in [False, True]:
        search.fill('ICM')
        expect(page.locator('#resource-ncpg')).to_be_hidden()
        link=page.locator('#directory-top a[href="#resource-ncpg"]')
        if keyboard:
            link.focus()
            page.keyboard.press('Enter')
        else:
            link.click()
        expect(search).to_have_value('')
        expect(page.locator('#resource-ncpg')).to_be_focused()
        expect(page.locator('[data-resource-card]:visible')).to_have_count(total)
    checks=[]
    for width in [320,390]:
        page.set_viewport_size({'width':width,'height':1000})
        for spaced in [False,True]:
            style=page.add_style_tag(content=TEXT_SPACING) if spaced else None
            for goal, heading in [('beginner','basics-heading'),('events','events-heading'),('tools','tools-heading')]:
                page.locator('[data-resource-goal="'+goal+'"]').click()
                expect(page.locator('#'+heading)).to_be_focused()
                page.wait_for_function("""id=>{
                  const r=document.getElementById(id).getBoundingClientRect();
                  const h=document.querySelector('.site-header').getBoundingClientRect();
                  return r.top>=h.bottom+8 && r.bottom<innerHeight;
                }""",arg=heading,timeout=5000)
                checks.append([width,spaced,goal])
            page.locator('#resource-reset').click()
            search.fill('ICM');search.press('Enter')
            page.wait_for_function("""()=>{
              const r=document.activeElement.getBoundingClientRect();
              return document.activeElement.tagName==='H2' &&
                r.top>=document.querySelector('.site-header').getBoundingClientRect().bottom+8 &&
                r.bottom<innerHeight;
            }""",timeout=5000)
            checks.append([width,spaced,'search'])
            search.fill('no-match-zzzz');search.press('Enter')
            expect(page.locator('#resource-count')).to_be_focused()
            page.wait_for_function("""()=>{
              const r=document.getElementById('resource-count').getBoundingClientRect();
              return r.top>=document.querySelector('.site-header').getBoundingClientRect().bottom+8 &&
                r.bottom<innerHeight;
            }""",timeout=5000)
            checks.append([width,spaced,'empty-search'])
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            if style:
                style.evaluate('(node)=>node.remove()')
    page.locator('#resource-reset').click()
    page.set_viewport_size({'width':1440,'height':1000})
    print(f'PASS: 7 modified/prevented click cases preserve state and native defaults; mouse and keyboard reveal; {len(checks)} mobile heading checks at 320/390px with normal and expanded text spacing.')
