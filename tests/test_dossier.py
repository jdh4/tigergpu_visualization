import sys
sys.path.append("../")
import unittest
from dossier import get_full_title
from dossier import make_dict
from dossier import get_position
from dossier import get_position_from_lines
from dossier import clean_position
from dossier import get_dept_code
from dossier import ldap_plus


class TestMakeDict(unittest.TestCase):

    def test_get_full_title(self):
        lines = ["dn: uid=rcar", "title: Professor of Chemistry and", " the PRISM", "field3: 42"]
        assert get_full_title(lines) == "Professor of Chemistry and the PRISM"
        lines = ["dn: uid=rcar", "title: Professor of Chemistry and", " the PRISM", " of NJ", "field3: 42"]
        assert get_full_title(lines) == "Professor of Chemistry and the PRISM of NJ"
        lines = ["dn: uid=rcar", "title: Professor of Chemistry"]
        assert get_full_title(lines) == "Professor of Chemistry"
        lines = ["dn: uid=rcar", "ou: Chemistry", "departmentNumber: 23500"]
        assert get_full_title(lines) == ""


class TestMakeDict(unittest.TestCase):

    def test_make_dict(self):
        lines = ["ignore this", "field1: value1", "title: value2", "field3: 42"]
        d = {"field1":["value1"], "title":["value2"], "field3":["42"]}
        assert d == dict(make_dict(lines))

        lines = ["field1: value1", "title: value2", "field1: 42"]
        d = {"field1":["value1", "42"], "title":["value2"]}
        assert d == dict(make_dict(lines))


class TestGetPosition(unittest.TestCase):

    def test_get_position(self):
        assert get_position("bigfoot") == "UNKNOWN"
        assert get_position("jdh4") == "Staff"
        assert get_position("jtromp") == "Faculty"
        assert get_position("eac") == "Faculty"
        assert get_position("pdebene") == "Dean (and Faculty)"


class TestGetPositionFromLines(unittest.TestCase):

    def test_get_position_from_lines(self):
        lines = ["pustatus: fac", "title: Professor of"]
        assert get_position_from_lines(lines) == "Faculty"

        lines = ["pustatus: fac", "title: Professor of", "pustatus: eme"]
        assert get_position_from_lines(lines) == "Faculty (emeritus)"

        lines = ["pustatus: fac", "pustatus: xfac"]
        assert get_position_from_lines(lines) == "UNKNOWN"

        lines = ["pustatus: fac", "pustatus: xfac", "title: Professor of"]
        assert get_position_from_lines(lines) == "Faculty"

        lines = ["pustatus: fac", "title: Lecturer"]
        assert get_position_from_lines(lines) == "Lecturer"

        lines = ["pustatus: fac", "title: Postdoc", "pustatus: stf"]
        assert get_position_from_lines(lines) == "Postdoc"

        lines = ["pustatus: fac", "pustatus: stf"]
        assert get_position_from_lines(lines) == "Staff"

        lines = ["title: Professor", "pustatus: xfac"]
        assert get_position_from_lines(lines) == "XFaculty"

        lines = ["puacademiclevel: G5", "pustatus: alumg"]
        assert get_position_from_lines(lines) == "Alumni (formerly G5)"

        lines = ["title: lecturer and postdoc"]
        assert get_position_from_lines(lines) == "Postdoc"

        lines = ["title: lecturer and research scholar"]
        assert get_position_from_lines(lines) == "Scholar"

        lines = ["pustatus: stp", "another line"]
        assert get_position_from_lines(lines) == "Short-Term Professional"


class TestCleanPosition(unittest.TestCase):

    def test_clean_position(self):
        assert clean_position("Scholar") == "Scholar"
        assert clean_position("Scholar", level=0) == "Scholar"
        assert clean_position("Postdoc (visiting)") == "Postdoc (visiting)"

        assert clean_position("Staff", level=1) == "Staff"
        assert clean_position("Postdoc (formerly G5)", level=1) == "Postdoc"
        assert clean_position("Scholar (visiting)", level=1) == "Scholar"
        assert clean_position("Faculty (emeritus)", level=1) == "Faculty"
 
        assert clean_position("DCU (formerly G7)", level=2) == "DCU"
        assert clean_position("Postdoc (formerly G7)", level=2) == "Postdoc"
        assert clean_position("G5", level=2) == "Graduate"
        assert clean_position("U2026", level=2) == "Undergrad"
        assert clean_position("XGraduate", level=2) == "XGraduate"

        assert clean_position("Faculty (emeritus)", level=3) == "Faculty"
        assert clean_position("Postdoc (visiting)", level=3) == "Postdoc"
        assert clean_position("DCU (formerly G5)", level=3) == "DCU/RCU/RU"
        assert clean_position("Lecturer", level=3) == "Staff"
        assert clean_position("XGraduate", level=3) == "Graduate"
        assert clean_position("XMiscAffil", level=3) == "XMiscAffil"


class TestGetDeptCode(unittest.TestCase):

    def test_get_dept_code(self):
        assert get_dept_code("Chemistry", "", "aturing") == "CHEM"
        assert get_dept_code("Unspecified Department", "Computer Science", "") == "CS"
        assert get_dept_code("Unspecified Department", "", "aturing") == "UNSPECIFIED"
        assert get_dept_code("Lewis-Sigler Institute for Integrative Genomics", "", "") == "LSI"
        assert get_dept_code("Undergraduate Class of 2026", "", "") == "U2026"
        assert get_dept_code("", "", "aturing") == "NOT_FOUND_IN_DOSSIER_DEPTS"
        assert get_dept_code("Santa Claus", "", "aturing") == "NOT_FOUND_IN_DOSSIER_DEPTS"
        assert get_dept_code("", "Santa Claus", "aturing") == "NOT_FOUND_IN_DOSSIER_DEPTS"
        assert get_dept_code("Electrical and Computer Engineering", "", "") == "ECE"
        assert get_dept_code("Electrical Engineering", "", "") == "ECE"


class TestLdapPlus(unittest.TestCase):

    def test_ldap_plus(self):
        assert ldap_plus(["cpena"])[1][0] == "Catherine J. Peña"
        assert ldap_plus(["cpena"])[1][2] == "Faculty"
