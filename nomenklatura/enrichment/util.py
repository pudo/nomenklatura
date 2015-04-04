from normality import normalize
from Levenshtein import jaro_winkler

from nomenklatura.core import db
from nomenklatura.model import Context, Entity
from nomenklatura.schema import types
from nomenklatura.model.constants import PENDING

SCORE_CUTOFF = 50


def text_score(match, candidates):
    if isinstance(candidates, basestring):
        candidates = [candidates]
    match_n = normalize(match)
    best_score = 0
    for candidate in candidates:
        cand_n = normalize(candidate)
        score = jaro_winkler(match_n, cand_n, 0.02) * 100
        best_score = max(int(score), best_score)
    return best_score


class LowScoreException(Exception):
    pass


class Spider(object):
    PUBLISHER_LABEL = None
    PUBLISHER_URL = None

    def create_context(self, root=None, url=None, score=None):
        ctx = Context.create(None, {
            'active': False,
            'source_url': url,
            'enrich_root': root,
            'enrich_score': score,
            'enrich_status': PENDING,
            'publisher': self.PUBLISHER_LABEL,
            'publisher_url': self.PUBLISHER_URL
        })
        ctx.score = score
        db.session.add(ctx)
        return ctx

    def scored_context(self, entity, title, url):
        score = text_score(title, entity.label)
        if score < SCORE_CUTOFF:
            return
        return self.create_context(root=entity.id, url=url,
                                   score=score)

    def create_entity(self, ctx, type_, **kwargs):
        # TODO: should this do lookups first?
        entity = Entity(assume_contexts=[ctx.id])
        entity.set(types.Object.attributes.type, type_, ctx)
        for attr in type_.attributes:
            if attr.name in kwargs:
                entity.set(attr, kwargs.get(attr.name), ctx)
        return entity

    def lookup(self, entity):
        pass