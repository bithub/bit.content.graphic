from plone.testing import z2

from plone.app.testing import PLONE_FIXTURE, TEST_USER_ID
from plone.app.testing import PloneSandboxLayer, IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.app.testing import setRoles, applyProfile


class TrinityContentGraphicTestLayer(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import bit.content.graphic
        self.loadZCML(package=bit.content.graphic)
        z2.installProduct(app, 'bit.content.graphic')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'bit.content.graphic:default')
        setRoles(portal, TEST_USER_ID, ['Manager'])

    def tearDownZope(self, app):
        z2.uninstallProduct(app, 'bit.content.graphic')

GRAPHIC_TEST_FIXTURE = TrinityContentGraphicTestLayer()
GRAPHIC_INTEGRATION_TESTING = IntegrationTesting(
    bases=(GRAPHIC_TEST_FIXTURE,),
    name="bit.content.graphic:integration")
GRAPHIC_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(GRAPHIC_TEST_FIXTURE,),
    name="bit.content.graphic:functional")
