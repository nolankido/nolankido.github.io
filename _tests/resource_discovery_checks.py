"""Reusable UI tests. Run over HTTP in CI or an explicitly described in-memory preview."""
import itertools
import json
from playwright.sync_api import expect


def check_discovery(page, root):
    entries = json.loads((root / '_source/poker/resources.json').read_text())['entries']
    import sys
    sys.path.insert(0, str(root / '_scripts'))
    import poker_resources as resources
    formats = ['all', *resources.FORMATS]
    levels = ['all', 'Beginner', 'Intermediate', 'Advanced', 'Technical']
    scenarios = []
    for fmt, level, free in itertools.product(formats, levels, [False, True]):
        expected = sorted('resource-' + e['id'] for e in entries
                          if (fmt == 'all' or resources.resource_format(e) == fmt)
                          and (level == 'all' or e['level'] in {level, 'All levels'})
                          and (not free or e['access'] == 'Free'))
        scenarios.append(dict(fmt=fmt, level=level, free=free, expected=expected))
    failures = page.evaluate('''(cases) => {
      const get=id=>document.getElementById(id), failures=[];
      for (const c of cases) {
        get('resource-reset').click();
        for (const [id,value] of [['resource-format',c.fmt],['resource-level',c.level]]) {
          get(id).value=value; get(id).dispatchEvent(new Event('change'));
        }
        if(c.free) get('resource-free').click();
        const cards=[...document.querySelectorAll('[data-resource-card]')];
        const actual=cards.filter(n=>!n.hidden&&!n.closest('[data-resource-section]').hidden).map(n=>n.id).sort();
        if(JSON.stringify(actual)!==JSON.stringify(c.expected)) failures.push({case:c,actual});
        const visible=actual.length;
        if(get('resource-count').textContent!==`${visible} of ${cards.length} resources shown.`) failures.push({count:c});
        if(get('resource-empty').hidden!==(visible!==0)) failures.push({empty:c});
        for(const button of document.querySelectorAll('[data-resource-filter]')) {
          const category=button.dataset.resourceFilter;
          const n=actual.filter(id=>category==='all'||get(id).dataset.category===category).length;
          if(!button.textContent.endsWith(`(${n})`)) failures.push({facet:category,case:c});
        }
      }
      get('resource-reset').click(); return failures;
    }''', scenarios)
    assert not failures, failures[:3]
    cards = page.locator('[data-resource-card]:visible')
    search = page.locator('#resource-search')
    page.locator('.resource-refine summary').click()
    page.locator('#resource-format').select_option('listen')
    page.locator('[data-resource-filter="watch-listen"]').click()
    expected = sum(e['category'] == 'watch-listen' and resources.resource_format(e) == 'listen' for e in entries)
    expect(cards).to_have_count(expected)
    page.locator('#resource-level').select_option('Technical')
    search.fill('no-match-zzzz')
    expect(page.locator('#resource-empty')).to_be_visible()
    # Starting choices replace incompatible filters and focus their result heading.
    page.locator('[data-resource-goal="beginner"]').click()
    expect(search).to_have_value('')
    expect(page.locator('#resource-level')).to_have_value('Beginner')
    expect(page.locator('#resource-format')).to_have_value('all')
    expect(page.locator('#resource-free')).to_have_attribute('aria-pressed', 'true')
    expect(page.locator('#basics-heading')).to_be_focused()
    expect(cards).to_have_count(sum(e['category']=='basics' and e['access']=='Free' and e['level'] in {'Beginner','All levels'} for e in entries))
    for goal, category in [('tournament','tournament-study'),('watch','watch-listen'),('tools','tools'),('events','events'),('variants','variants')]:
        page.locator('[data-resource-goal="'+goal+'"]').click()
        expect(cards).to_have_count(sum(e['category']==category for e in entries))
        expect(page.locator('#'+category+'-heading')).to_be_focused()
    page.locator('#resource-reset').click()
    search.fill('ICM'); search.press('Enter')
    expect(page.locator('#resource-icm-basics')).to_be_visible()
    assert page.evaluate('document.activeElement.tagName') == 'H2'
    before = cards.count()
    page.locator('#resource-compact').click()
    expect(page.locator('#resource-compact')).to_have_attribute('aria-pressed','true')
    expect(cards).to_have_count(before)
    # Compact and print must never suppress the heads-up model restriction.
    search.fill('heads up'); search.press('Enter')
    expect(page.locator('#resource-hu-push-fold .resource-caution')).to_be_visible()
    expect(page.locator('#resource-hu-push-fold .resource-caution')).to_contain_text('six-player')
    page.evaluate('window.dispatchEvent(new Event("beforeprint"))')
    expect(cards).to_have_count(len(entries))
    page.evaluate('window.dispatchEvent(new Event("afterprint"))')
    expect(page.locator('#resource-hu-push-fold')).to_be_visible()
    expect(page.locator('#resource-omaha-rules')).to_be_hidden()
    page.locator('#resource-compact').click()
    page.locator('#resource-reset').click()
    # The empty view does not hide links to support services.
    search.fill('no-match-zzzz'); expect(page.locator('#resource-empty')).to_be_visible()
    expect(page.locator('#directory-top a[href="#resource-ncpg"]')).to_be_visible()
    expect(page.locator('#directory-top a[href="#resource-gamcare-support"]')).to_be_visible()
    page.locator('#resource-reset').click()
    print(f'PASS: {len(scenarios)} format/experience/free combinations with independent catalogue counts, facet counts, 6 starting choices, keyboard result focus, compact caution visibility, print restoration and always-available support links.')
