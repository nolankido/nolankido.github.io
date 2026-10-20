"""Retain actionable axe uncertainty without calling it an accessibility pass.

This module serializes test diagnostics only. It deliberately omits node HTML,
free-form messages and data, URLs, and element text. It does not certify WCAG
conformance or provide evidence about a human participant.
"""
from copy import deepcopy


CHECK_GROUPS = ('any', 'all', 'none')


def _text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(field + ' must be nonempty text')
    return value


def _target(value):
    # axe may describe frames and shadow roots using nested selector arrays.
    if not isinstance(value, list) or not value:
        raise ValueError('axe target must be a nonempty selector array')
    for part in value:
        if isinstance(part, list):
            _target(part)
        else:
            _text(part, 'axe selector')
    return deepcopy(value)


def _rules(value, field):
    if not isinstance(value, list):
        raise ValueError(field + ' must be an array')
    for item in value:
        if not isinstance(item, dict):
            raise ValueError(field + ' entries must be objects')
        _text(item.get('id'), field + ' rule id')
    return value


def incomplete_evidence(result, *, page_path, width, scope, javascript):
    """Return review records for each incomplete rule, never inferred passes.

    page_path and scope are explicit test configuration, not a URL inferred
    from the remote browser. The caller must not use real participant inputs.
    """
    if not isinstance(result, dict):
        raise ValueError('axe result must be an object')
    _rules(result.get('violations'), 'violations')
    items = _rules(result.get('incomplete'), 'incomplete')
    if (not isinstance(page_path, str) or not page_path.startswith('/')
            or page_path.startswith('//') or '?' in page_path or '#' in page_path):
        raise ValueError('page_path must be a local path without a query or fragment')
    if type(width) is not int or width < 1:
        raise ValueError('width must be a positive integer')
    _text(scope, 'scope')
    if type(javascript) is not bool:
        raise ValueError('javascript must be a boolean')
    records = []
    for item in items:
        nodes = item.get('nodes')
        if not isinstance(nodes, list) or not nodes:
            raise ValueError('incomplete rule must identify its nodes')
        saved = []
        for node in nodes:
            if not isinstance(node, dict):
                raise ValueError('axe node must be an object')
            checks = {}
            for group in CHECK_GROUPS:
                source = node.get(group)
                if not isinstance(source, list):
                    raise ValueError('axe check group ' + group + ' must be an array')
                checks[group] = []
                for check in source:
                    if not isinstance(check, dict):
                        raise ValueError('axe check must be an object')
                    related = check.get('relatedNodes', [])
                    if not isinstance(related, list):
                        raise ValueError('relatedNodes must be an array')
                    targets = []
                    for other in related:
                        if not isinstance(other, dict):
                            raise ValueError('related node must be an object')
                        targets.append(_target(other.get('target')))
                    checks[group].append({
                        'id': _text(check.get('id'), 'check id'),
                        'related_targets': targets,
                    })
            saved.append({'target': _target(node.get('target')), 'checks': checks})
        impact = item.get('impact')
        if impact not in (None, 'minor', 'moderate', 'serious', 'critical'):
            raise ValueError('unrecognized axe impact')
        records.append({
            'path': page_path, 'width': width, 'javascript': javascript,
            'scope': scope, 'id': item['id'], 'impact': impact,
            'review_status': 'manual_review_required', 'nodes': saved,
        })
    return records


def accessibility_status(scans, violations, incomplete):
    """Describe automated coverage separately from functional test status."""
    if type(scans) is not int or scans < 0:
        raise ValueError('scan count must be a nonnegative integer')
    if not isinstance(violations, list) or not isinstance(incomplete, list):
        raise ValueError('findings must be arrays')
    if scans == 0:
        if violations or incomplete:
            raise ValueError('findings require an executed scan')
        return 'not_run'
    if violations:
        return 'violations_found'
    if incomplete:
        return 'manual_review_required'
    return 'no_automated_findings'
