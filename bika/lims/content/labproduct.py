from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.CMFCore.permissions import View, ModifyPortalContent
from bika.lims.config import I18N_DOMAIN, PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from decimal import Decimal
from bika.lims import bikaMessageFactory as _

schema = BikaSchema.copy() + Schema((
    StringField('Volume',
        widget = StringWidget(
            label = _("Volume"),
        )
    ),
    StringField('Unit',
        widget = StringWidget(
            label = _("Unit"),
        )
    ),
    FixedPointField('VAT',
        default_method = 'getDefaultVAT',
        widget = DecimalWidget(
            label = _("VAT %"),
            description = _("Enter percentage value eg. 14"),
        ),
    ),
    FixedPointField('Price',
        widget = DecimalWidget(
            label = _("Price excluding VAT"),
        )
    ),
    ComputedField('VATAmount',
        expression = 'context.getVATAmount',
        widget = ComputedWidget(
            label = _("VAT"),
            visible = {'edit':'hidden', }
        ),
    ),
    ComputedField('TotalPrice',
        expression = 'context.getTotalPrice()',
        widget = ComputedWidget(
            label = _("Total price"),
            visible = {'edit':'hidden', }
        ),
    ),
))

schema['description'].schemata = 'default'
schema['description'].widget.visible = True

class LabProduct(BaseContent):
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    def getTotalPrice(self):
        """ compute total price """
        price = self.getPrice()
        if not price:
            print "not price"
        price = Decimal(price or '0.00')
        vat = Decimal(self.getVAT())
        price = price and price or 0
        vat = vat and vat / 100 or 0
        price = price + (price * vat)
        return price.quantize(Decimal('0.00'))

    def getDefaultVAT(self):
        """ return default VAT from bika_setup """
        try:
            vat = self.bika_setup.getVAT()
            return vat
        except ValueError:
            return "0.00"

    security.declarePublic('getVATAmount')
    def getVATAmount(self):
        """ Compute VATAmount
        """
        try:
            vatamount = self.getTotalPrice() - Decimal(self.getPrice())
        except:
            vatamount = Decimal('0.00')
        return vatamount.quantize(Decimal('0.00'))

registerType(LabProduct, PROJECTNAME)
