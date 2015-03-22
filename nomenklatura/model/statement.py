from sqlalchemy.ext.hybrid import hybrid_property

from nomenklatura.core import db
from nomenklatura.model.schema import attributes
from nomenklatura.model.common import CommonMixIn, KEY_LENGTH


class Statement(db.Model, CommonMixIn):
    """ Statements are facts that relate to an entity. Each statement
    has a subject (the entity), an attribute (a predefined, typed
    property name) and an object (the value of the statement). """

    __tablename__ = 'statement'

    subject = db.Column(db.String(KEY_LENGTH))
    _attribute = db.Column('attribute', db.String(1024))
    _value = db.Column('value', db.Unicode)

    dataset_id = db.Column(db.String(KEY_LENGTH), db.ForeignKey('dataset.id'))
    dataset = db.relationship('Dataset', backref=db.backref('statements',
                              lazy='dynamic', cascade='all, delete-orphan')) # noqa

    context_id = db.Column(db.String(KEY_LENGTH), db.ForeignKey('context.id'),
                           nullable=True)
    context = db.relationship('Context', backref=db.backref('statements',
                         lazy='dynamic', cascade='all, delete-orphan')) # noqa

    def __init__(self, dataset, subject, attribute, value, context=None):
        self.dataset = dataset
        self.subject = subject
        self.attribute = attribute
        self.value = value
        self.context = context

    @hybrid_property
    def attribute(self):
        return attributes[self._attribute]

    @attribute.setter
    def attribute(self, attr):
        if hasattr(attr, 'name'):
            attr = attr.name
        self._attribute = attr

    @hybrid_property
    def value(self):
        return self.attribute.converter().deserialize(self._value)

    @value.setter
    def value(self, value):
        self._value = self.attribute.converter().serialize(value)

    @property
    def active(self):
        return True

    def to_dict(self):
        return {
            'id': self.id,
            'subject': self.subject.id,
            'attribute': self.attribute.name,
            'value': self.value,
            'context_id': self.context_id,
            'dataset_id': self.dataset_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def __cmp__(self, other):
        if other is None:
            return 1
        # active checks
        return cmp(self.updated_at, other.updated_at)

    def __repr__(self):
        return u'<Statement(%s,%s,%r)>' % (self.subject, self.attribute,
                                           self.value)

    def __unicode__(self):
        return self.object