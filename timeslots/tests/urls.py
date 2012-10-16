from django.core.urlresolvers import RegexURLPattern, Resolver404, get_resolver
from django.core import urlresolvers
from django.http import HttpResponse

__all__ = ('resolve_to_name',)

intro_text = """Named URL patterns for the {% url %} tag
========================================

e.g. {% url pattern-name %}
or   {% url pattern-name arg1 %} if the pattern requires arguments

"""


def show_url_patterns(request):
    patterns = _get_named_patterns()
    r = HttpResponse(intro_text, content_type='text/plain')
    longest = max([len(pair[0]) for pair in patterns])
    for key, value in patterns:
        r.write('%s %s\n' % (key.ljust(longest + 1), value))
    return r


def _get_named_patterns():
    "Returns list of (pattern-name, pattern) tuples"
    resolver = urlresolvers.get_resolver(None)
    patterns = sorted([
        (key, value[0][0][0])
        for key, value in resolver.reverse_dict.items()
        if isinstance(key, basestring)
    ])
    return patterns


def _parse_match(match):
    args = list(match.groups())
    kwargs = match.groupdict()
    for val in kwargs.values():
        args.remove(val)
    return args, kwargs


def _pattern_resolve_to_name(self, path):
    match = self.regex.search(path)
    if match:
        name = ""
        if self.name:
            name = self.name
        elif hasattr(self, '_callback_str'):
            name = self._callback_str
        else:
            name = "%s.%s" % (self.callback.__module__,
                              self.callback.func_name)
        args, kwargs = _parse_match(match)
        return name, args, kwargs


def _resolver_resolve_to_name(self, path):
    tried = []
    match = self.regex.search(path)
    if match:
        new_path = path[match.end():]
        for pattern in self.url_patterns:
            try:
                if isinstance(pattern, RegexURLPattern):
                    nak = _pattern_resolve_to_name(pattern, new_path)
                else:
                    nak = _resolver_resolve_to_name(pattern, new_path)
            except Resolver404, e:
                tried.extend([(pattern.regex.pattern + '   ' + t) for t in e.args[0]['tried']])
            else:
                if nak:
                    return nak  # name, args, kwargs
                tried.append(pattern.regex.pattern)
        raise Resolver404, {'tried': tried, 'path': new_path}


def resolve_to_name(path, urlconf=None):
    r = get_resolver(urlconf)
    if isinstance(r, RegexURLPattern):
        return _pattern_resolve_to_name(r, path)
    else:
        return _resolver_resolve_to_name(r, path)
