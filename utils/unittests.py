from Util.UtilGAE import FixSysPath
FixSysPath()

import unittest
import sys
import webtest #pip install webTest; http://webtest.pythonpaste.org/en/latest/
import webapp2
import os
import pprint
import xml.dom.minidom
import urlparse
from HTMLParser import HTMLParser
from google.appengine.ext import testbed

WEBSITE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
sys.path.append(WEBSITE_DIR)
import main

def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)

def GetTextAllNodesByNameFromFile(filePath, tagName):
    """
    This helper function will return all the elements' text in a file with a specific tag.
    """
    dom = xml.dom.minidom.parse(filePath)
    elements = dom.getElementsByTagName(tagName)
    assert (len(elements)> 0), "<" + tagName + "> does not exist in " + filePath
    elements = [getText(x.childNodes) for x in elements]
    return elements

def RemoveTheseHandlersFromRoute(routes, listOfIgnoredHandlers):
    #Ignore some of the routes which you dont want to test
    tempRoutes = []
    for x in main.GLOBAL_ROUTES:
        if x[1] not in listOfIgnoredHandlers:
            tempRoutes.append(x)
    return tempRoutes

def KeepOnlyTheseHandlers(routes, listOfDesiredHandlers):
    #Ignore some of the routes which you dont want to test
    tempRoutes = []
    for x in main.GLOBAL_ROUTES:
        if x[1] in listOfDesiredHandlers:
            tempRoutes.append(x)
    return tempRoutes

class PermanentRedirectsTests(unittest.TestCase):
    def setUp(self):
        self.testRoutes = KeepOnlyTheseHandlers(main.GLOBAL_ROUTES,
                [main.PermanentRedirects])
        #Create a WSGI application
        app = webapp2.WSGIApplication(self.testRoutes, debug=True)
        #Wrap the app with the WebTest's TestApp
        self.testapp = webtest.TestApp(app)

    def test_ResponseCodeCheck(self):
        for eachRoute in self.testRoutes:
            resp = self.testapp.get(eachRoute[0])
            self.assertEqual(resp.status_code, 301)
        return



def ListOfUrlsInThisHTMLResp(resp):
    class LinkFinder(HTMLParser):
        """A subclass of HTMLParser for proper parsing of pages."""
        def __init__(self):
            HTMLParser.__init__(self)
            self._suburls = list() #Contatins list of all the urls that appeared on this page

        def handle_starttag(self, tag, attrs):
            if tag.lower() == 'a':
                for (att, val) in attrs:
                    if att.lower() == "href":
                        self._suburls.append(val)

        def get_suburls(self):
            return self._suburls

    lf = LinkFinder()
    lf.feed(resp)
    return lf.get_suburls()

class LocalTests(unittest.TestCase):
    def setUp(self):
        self.testRoutes = RemoveTheseHandlersFromRoute(main.GLOBAL_ROUTES,
                [main.WarmupQueryHandler, main.PermanentRedirects])
        #Create a WSGI application
        app = webapp2.WSGIApplication(self.testRoutes, debug=True)
        #Wrap the app with the WebTest's TestApp
        self.testapp = webtest.TestApp(app, extra_environ=dict(HTTP_USER_AGENT='Chrome'))

        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_taskqueue_stub()

    def crawlableUrlsList(self):
        scannedUrls = list()
        unScannedUrls = ["/", ]

        while unScannedUrls:
            url = unScannedUrls.pop()
            if url in scannedUrls: continue
            #import pdb; pdb.set_trace()
            resp = self.testapp.get(url)
            self.assertEqual(resp.status, "200 OK")
            self.assertEqual(resp.status_code, 200)
            for subUrl in ListOfUrlsInThisHTMLResp(resp.body):
                if subUrl.lower().startswith("http"): continue #TODO: Hack. It means it is an outbound url and does not reside on our doamin
                if subUrl in scannedUrls: continue
                if subUrl in unScannedUrls: continue
                if subUrl == url: continue

                unScannedUrls.append(subUrl)
            scannedUrls.append(url)

        return scannedUrls



    def test_TitlePresenceInHTMLS(self):
        #Each html should have a title tag
        for eachRoute in self.testRoutes:
            resp = self.testapp.get(eachRoute[0])
            resp.mustcontain("<title>")
        return

    def test_DescriptionsPresenceInHTMLS(self):
        #Each html should have a description tag
        for eachRoute in self.testRoutes:
            resp = self.testapp.get(eachRoute[0])
            resp.mustcontain("<meta name=\"description\"")
            #TODO: Ensure the description is more than 60 and less than a bigger limit like 160
        return
    def test_DescriptionsAccuracy(self):
        #TODO: Ensure that each word in description is mentioned atleast once in the body.

        return

    def test_TitleAccuracy(self):
        #TODO: Ensure that each word in title is mentioned at least once in the body.
        return

    def test_HTMLSitemmapIntegrity(self):
        """
        Tests whether html sitemap contanins all the links which are present in GLOBAL_ROUTES
        """
        #TODO: It takes into account all the links on the page including navigation bar. It represents a bug since some of the links in navigation bar are not rendered in mobile view and are simply set to display: none while still being present in html.
        listOfSitemapUrls = ListOfUrlsInThisHTMLResp(self.testapp.get("/sitemap").body)
        siteMapUrlsAsText = [urlparse.urlparse(l).path for l in listOfSitemapUrls]
        locSet = frozenset(siteMapUrlsAsText)
        routesSet = frozenset(self.crawlableUrlsList())
        orphans = locSet.symmetric_difference(routesSet)
        self.assertEqual(len(orphans), 0, "Crawlable links and HTML sitemap has dissimalrity wrt following elelments:\n{}".format(pprint.pformat(orphans)))
        return

    def test_XMLSitemmapIntegrity(self):
        """
        Tests whether xml sitemap contanins all the links which are present in GLOBAL_ROUTES
        """
        sitemapXMLPath = os.path.join(WEBSITE_DIR, "static", "sitemap.xml")
        locationsAsText = GetTextAllNodesByNameFromFile(sitemapXMLPath, "loc")
        pathsAsText = [urlparse.urlparse(l).path for l in locationsAsText]
        locSet = frozenset(pathsAsText)
        routesSet = frozenset([x[0] for x in self.testRoutes])
        orphans = locSet.symmetric_difference(routesSet)
        self.assertEqual(len(orphans), 0, "Routes and sitemap has dissimalrity wrt following elelments:\n{}".format(pprint.pformat(orphans)))
        return

    def test_NoCrawlErrors(self):
        for url in self.crawlableUrlsList():
            resp = self.testapp.get(url)
            self.assertEqual(resp.status, "200 OK")
            self.assertEqual(resp.status_code, 200)



class W3InternetValidationOfAllPages(unittest.TestCase):
    def setUp(self):
        self.testRoutes = RemoveTheseHandlersFromRoute(main.GLOBAL_ROUTES,
                [main.WarmupQueryHandler, main.PermanentRedirects])

    def testW3pages(self):
        from py_w3c.validators.html.validator import HTMLValidator
        for eachRoute in self.testRoutes:
            vld = HTMLValidator()
            resp = self.testapp.get(eachRoute[0])
            vld.validate_fragment(resp)
            if len(vld.errors) > 0 :
                print("Errors in page {}\n{}\n{}".format(eachRoute[0], "_"*60, pprint.pformat(vld.errors)))


if __name__ == '__main__':
    #for x in [LocalTests, PermanentRedirectsTests]:
    #   unittest.TextTestRunner(verbosity=1).run(unittest.TestLoader().loadTestsFromTestCase(x))

    #if raw_input("Execute W3 validation on global pages(y/n)").lower() == 'y':
    #    unittest.TextTestRunner(verbosity=2).run(unittest.TestLoader().loadTestsFromTestCase(W3InternetValidationOfAllPages))
    pass
