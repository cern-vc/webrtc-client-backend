from sqlalchemy.exc import IntegrityError, InvalidRequestError
from app import db
from app.browser_handling.tests import ModelTestCase

# your test cases
from app.browser_handling.models import OperatingSystem, OperatingSystemFactory


class OperatingSystemTest(ModelTestCase):

    def add_test_oss(self):
        windows_xp = OperatingSystem(name="Windows XP")
        windows_7 = OperatingSystem(name="Windows 7")
        windows_10 = OperatingSystem(name="Windows 10")
        mac_os_x_cap = OperatingSystem(name="Mac OS X El Capitan")
        mac_os_x_yos = OperatingSystem(name="Mac OS X El Yosemite")
        ubuntu_14 = OperatingSystem(name="Ubuntu 14.04")
        slc_6 = OperatingSystem(name="CERN Scientific Linux 6")
        cern_centos_7 = OperatingSystem(name="CERN Centos 7")

        db.session.add(windows_xp)
        db.session.add(windows_7)
        db.session.add(windows_10)
        db.session.add(mac_os_x_cap)
        db.session.add(mac_os_x_yos)
        db.session.add(ubuntu_14)
        db.session.add(slc_6)
        db.session.add(cern_centos_7)
        db.session.commit()

    def test_add_os(self):

        windows = OperatingSystem(name="Windows XP")
        db.session.add(windows)
        db.session.commit()

        # this works
        assert windows in db.session

    def test_remove_os(self):

        windows = OperatingSystem(name="Windows XP")
        db.session.add(windows)
        db.session.commit()

        # this works
        assert windows in db.session

        db.session.delete(windows)
        db.session.commit()

        # this works
        assert windows not in db.session

    def test_add_twice_os(self):

        windows = OperatingSystem(name="Windows XP")
        db.session.add(windows)
        db.session.commit()

        windows2 = OperatingSystem(name="Windows XP")
        db.session.add(windows2)
        try:
            db.session.commit()
            assert None
        except IntegrityError:
            db.session.rollback()
            assert True

        windows_found = OperatingSystem.query.filter_by(name="Windows XP").one()
        # this works
        assert windows_found in db.session

    def test_remove_unexisting_os(self):

        windows = OperatingSystem(name="Windows XP")
        try:
            db.session.delete(windows)
        except InvalidRequestError:
            assert True
        db.session.commit()

        # this works
        assert windows not in db.session


class OperatingSystemFactoryTest(ModelTestCase):

    def test_add_os(self):

        windows = OperatingSystemFactory.create_operating_system("Windows XP", save=False)
        OperatingSystemFactory.save_operating_system(windows)

        # this works
        assert windows in db.session

    def test_delete_os(self):

        windows = OperatingSystemFactory.create_operating_system("Windows XP", save=True)
        # this works
        assert windows in db.session

        was_deleted = OperatingSystemFactory.delete_operating_system(windows)

        # this works
        assert was_deleted

    def test_add_twice_os(self):

        OperatingSystemFactory.create_operating_system("Windows XP", save=True)

        windows2 = OperatingSystemFactory.create_operating_system("Windows XP", save=True)
        assert windows2 is  not None

        windows_found = OperatingSystemFactory.find_by_name("Windows XP")
        # # this works
        assert windows_found in db.session

    def test_remove_nonexisting_os(self):

        windows = OperatingSystemFactory.create_operating_system("Windows XP")

        windows_found = OperatingSystemFactory.delete_operating_system(windows)

        # this works
        assert windows_found

    def test_find_existing(self):
        OperatingSystemFactory.create_operating_system("Windows XP", save=True)
        windows2 = OperatingSystemFactory.create_operating_system("Windows XP 2", save=True)

        windows_found = OperatingSystemFactory.find_by_name("Windows XP")
        # # this works
        assert windows_found
        assert windows_found != windows2