# -*- coding: utf-8 -*-
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.recycleview.datamodel import RecycleDataModelBehavior, RecycleDataModel
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.properties import ObjectProperty, AliasProperty
from kivy.factory import Factory
from kivy.clock import Clock

from kivy.graphics import Color, Line


from kivy.lang import Builder
Builder.load_string('''
#:import SlideTransition kivy.uix.screenmanager.SlideTransition

<PageView>:
    viewclass: ''
    data: []
    transition: SlideTransition(direction='left')
    layout1: layout1
    layout2: layout2
    layout: layout1

    rows: 1
    cols: 1
    total: self.rows * self.cols

    page: 0
    maxpage: int((len(self.data) - 1) / self.total) + 1

    wspace: 0
    hspace: 0

    wedge: 0
    hedge: 0

    child_width: (self.width - 2 * self.wedge + self.wspace) / self.cols - self.wspace
    child_height: (self.height - 2 * self.hedge + self.hspace) / self.rows - self.hspace
    child_size: (self.child_width, self.child_height)

    Screen:
        name: 'layout1'
        GridLayout:
            id: layout1
            rows: root.rows
            cols: root.cols
            spacing: (root.wspace, root.hspace)
            pos: (root.wedge, -root.hedge)
    Screen:
        name: 'layout2'
        GridLayout:
            id: layout2
            rows: root.rows
            cols: root.cols
            spacing: (root.wspace, root.hspace)
            pos: (root.wedge, -root.hedge)
''')


class PageViewBehavior(object):
    _data_model = None
    _refresh_trigger = None

    def __init__(self, **kwargs):
        self._refresh_trigger = Clock.create_trigger(self.refresh_views, -1)
        super(PageViewBehavior, self).__init__(**kwargs)

    def refresh_views(self, *largs):
        data = self.data[self.page * self.total: (self.page + 1) * self.total]

        for widget in self.layout.children:
            widget.size = self.child_size
            widget.size_hint = (None, None)
            widget.opacity = 0

        for widget, d in zip(self.layout.children[::-1], data):
            widget.opacity = 1
            for k, v in d.items():
                setattr(widget, k, v)

        #下方的小圆点
        with self.canvas:
            for i in range(self.maxpage):
                x = self.width / 2 + (i - self.maxpage / 2) * self.width / 32
                y = self.hedge / 2
                if i == self.page:
                    Color(rgba=(1, 1, 1, 1))
                else:
                    Color(rgba=(0.5, 0.5, 0.5, 1))
                Line(circle=(x, y, self.hedge / 15), width=3)

    def refresh_from_data(self, *largs, **kwargs):
        self._refresh_trigger()

    def _dispatch_prop_on_source(self, prop_name, *largs):
        # Dispatches the prop of this class when the
        # view_adapter/layout_manager property changes.
        getattr(self.__class__, prop_name).dispatch(self)

    def _get_data_model(self):
        return self._data_model

    def _set_data_model(self, value):
        data_model = self._data_model
        if value is data_model:
            return
        if data_model is not None:
            self._data_model = None
            data_model.detach_recycleview()

        if value is None:
            return True

        if not isinstance(value, RecycleDataModelBehavior):
            raise ValueError(
                'Expected object based on RecycleDataModelBehavior, got {}'.
                format(value.__class__))

        self._data_model = value
        value.attach_recycleview(self)
        self.refresh_from_data()
        return True

    data_model = AliasProperty(_get_data_model, _set_data_model)

    def layout_change(self):
        if self.layout == self.layout1:
            self.layout = self.layout2
            self.current = 'layout2'
        elif self.layout == self.layout2:
            self.layout = self.layout1
            self.current = 'layout1'
        self.refresh_from_data()

    def page_prev(self):
        if self.page > 0:
            self.page -= 1
            self.transition = SlideTransition(direction='right')
            self.layout_change()

    def page_next(self):
        if self.page < self.maxpage - 1:
            self.page += 1
            self.transition = SlideTransition(direction='left')
            self.layout_change()


class PageView(PageViewBehavior, ScreenManager, FloatLayout):
    viewclass = ObjectProperty(None)

    def _get_data(self):
        d = self.data_model
        return d and d.data

    def _set_data(self, value):
        d = self.data_model
        if d is not None:
            d.data = value

    data = AliasProperty(_get_data, _set_data, bind=['data_model'])

    def on_touch_down(self, touch):
        super(PageView, self).on_touch_down(touch)
        self._down_pos = touch.pos
        return True

    def on_touch_up(self, touch):
        dx, dy = self._down_pos
        ux, uy = touch.pos

        if abs(dx - ux) < 2 * abs(dy - uy):
            super(PageView, self).on_touch_up(touch)
            return False
        if abs(dx - ux) < 0.05 * self.width:
            super(PageView, self).on_touch_up(touch)
            return False

        if dx - ux > 0:
            self.page_next()
        else:
            self.page_prev()
        return True

    def __init__(self, **kwargs):
        if self.data_model is None:
            kwargs.setdefault('data_model', RecycleDataModel())
        super(PageView, self).__init__(**kwargs)

        self.viewclass = getattr(Factory, self.viewclass)
        for i in range(self.total):
            self.layout1.add_widget(self.viewclass())
            self.layout2.add_widget(self.viewclass())
