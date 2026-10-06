# Website analytics

Installed October 6, 2026. The owner supplied the Umami Cloud website ID.
The tracking script is in `_source/layout.html` and is emitted once in the
head of each public HTML page, including the custom 404. Future generated
pages inherit it. Do not paste another copy into individual page bodies.

## Scope and privacy

- Pageviews only; no advertising pixels, session recordings, user IDs,
  custom event properties, or form-field instrumentation are added.
- `data-domains` permits `nolankido.com` and `www.nolankido.com`; local
  previews and alternate development hostnames do not send pageviews.
- `data-do-not-track="true"` respects the browser Do Not Track preference.
- `data-exclude-search="true"` and `data-exclude-hash="true"` omit query
  strings and fragments from recorded page URLs. This intentionally
  sacrifices query-based campaign/UTM analysis in the initial setup.
- The deferred external script is optional. The site does not call Umami
  from its contact JavaScript, and blocked analytics must not break use.
- The website ID is a public tracker identifier, not an account password
  or private API key. Never commit account credentials or private keys.

Umami's documented standard tracking is cookie-free. Loading the script
and sending requests still involves a network connection to the provider;
do not describe this as collecting no information at all. The public
privacy page discloses analytics separately from hosting, fonts and forms.
This implementation is not a blanket legal-compliance certification.

## Verification and maintenance

Run the existing build, unit and browser checks. `test_analytics.py`
validates coverage, duplicate prevention, the exact website ID and
privacy attributes without sending synthetic events to production.
The ordinary Site checks workflow stays read-only.

After Pages deployment, open the Umami dashboard for `nolankido.com`,
visit a public page and check that a pageview appears. Browser blockers
or Do Not Track may exclude a test visit. Successful publication and a
valid script tag do not by themselves prove ingestion into the private
dashboard. Do not claim ingestion is verified without observing it.

YouTube clicks, downloads, contact acceptance events and Google Search
Console are not configured by this initial installation. Add only
explicitly named, non-personal events when they have a defined use, and
update the public notice and regression tests at the same time.

References:
- https://docs.umami.is/docs/collect-data
- https://docs.umami.is/docs/tracker-configuration
- https://docs.umami.is/docs/faq
- https://umami.is/privacy
