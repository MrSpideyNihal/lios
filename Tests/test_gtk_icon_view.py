#!/usr/bin/env python3
"""
Tests for lios/ui/gtk/icon_view.py (IconView)
──────────────────────────────────────────────
Covers: instantiation, model setup, add_item with real images,
        select_all_items, get_selected_item_names, invert_list,
        clear via remove, signal connections.
"""
import logging
import os
import pytest

logger = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def gtk_init():
    import gi
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk
    Gtk.init([])


@pytest.fixture
def icon_view(gtk_init):
    from lios.ui.gtk.icon_view import IconView
    return IconView()


@pytest.fixture
def test_image(tmp_path):
    """Create a small test PNG and return its path."""
    import gi
    gi.require_version("Gtk", "3.0")
    from gi.repository import GdkPixbuf
    path = str(tmp_path / "test_icon.png")
    pixbuf = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, False, 8, 50, 50)
    pixbuf.fill(0xFF0000FF)
    pixbuf.savev(path, "png", [], [])
    return path


@pytest.fixture
def two_images(tmp_path):
    """Create two test PNGs and return their paths."""
    import gi
    gi.require_version("Gtk", "3.0")
    from gi.repository import GdkPixbuf
    paths = []
    for i, color in enumerate([0xFF0000FF, 0x00FF00FF]):
        path = str(tmp_path / f"img_{i}.png")
        pixbuf = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, False, 8, 60, 40)
        pixbuf.fill(color)
        pixbuf.savev(path, "png", [], [])
        paths.append(path)
    return paths


# ═══════════════════════════════════════════════════════════════════════════
class TestIconViewBasic:
    def test_instantiation(self, icon_view):
        assert icon_view is not None

    def test_default_model_empty(self, icon_view):
        model = icon_view.get_model()
        assert len(model) == 0

    def test_selection_mode_is_multiple(self, icon_view):
        import gi
        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk
        assert icon_view.get_selection_mode() == Gtk.SelectionMode.MULTIPLE

    def test_invert_callback_default_none(self, icon_view):
        assert icon_view.on_invert_list_callback is None


# ═══════════════════════════════════════════════════════════════════════════
class TestIconViewAddItem:
    def test_add_item_increases_model(self, icon_view, test_image):
        icon_view.add_item(test_image)
        model = icon_view.get_model()
        assert len(model) == 1

    def test_add_item_stores_filename(self, icon_view, test_image):
        icon_view.add_item(test_image)
        model = icon_view.get_model()
        stored_name = model[0][1]
        assert stored_name == test_image

    def test_add_multiple_items(self, icon_view, two_images):
        icon_view.add_item(two_images[0])
        icon_view.add_item(two_images[1])
        assert len(icon_view.get_model()) == 2

    def test_add_nonexistent_file_no_crash(self, icon_view):
        icon_view.add_item("/tmp/nonexistent_image_xyz.png")
        # Should silently skip via except:pass
        assert len(icon_view.get_model()) == 0


# ═══════════════════════════════════════════════════════════════════════════
class TestIconViewSelect:
    def test_select_all_items(self, icon_view, two_images):
        icon_view.add_item(two_images[0])
        icon_view.add_item(two_images[1])
        icon_view.select_all_items()
        selected = icon_view.get_selected_items()
        assert len(selected) == 2

    def test_get_selected_item_names(self, icon_view, two_images):
        icon_view.add_item(two_images[0])
        icon_view.add_item(two_images[1])
        icon_view.select_all_items()
        names = icon_view.get_selected_item_names()
        assert len(names) == 2
        assert two_images[0] in names
        assert two_images[1] in names


# ═══════════════════════════════════════════════════════════════════════════
class TestIconViewInvert:
    def test_invert_list_reverses_order(self, icon_view, two_images):
        icon_view.add_item(two_images[0])
        icon_view.add_item(two_images[1])
        model_before = [row[1] for row in icon_view.get_model()]
        icon_view.invert_list()
        model_after = [row[1] for row in icon_view.get_model()]
        assert model_after == list(reversed(model_before))

    def test_invert_list_callback_called(self, icon_view, two_images):
        called = []
        icon_view.on_invert_list_callback = lambda: called.append(True)
        icon_view.add_item(two_images[0])
        icon_view.invert_list()
        assert len(called) == 1

    def test_invert_list_no_callback_no_crash(self, icon_view, two_images):
        icon_view.on_invert_list_callback = None
        icon_view.add_item(two_images[0])
        icon_view.invert_list()  # Should not crash


# ═══════════════════════════════════════════════════════════════════════════
class TestIconViewSignals:
    def test_connect_on_selected_callback(self, icon_view):
        icon_view.connect_on_selected_callback(lambda *a: None)

    def test_enable_delete_key_no_crash(self, icon_view):
        icon_view.enable_delete_key()
