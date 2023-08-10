# -*- coding: utf-8 -*-

# This code is part of Qiskit.
#
# (C) Copyright IBM 2017, 2021.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

# Contributors: Figen YILMAZ, Li-Chieh Hsiao, Christian Kraglund Andersen
"""Transmon Pocket Teeth.
"""

import numpy as np
from qiskit_metal import draw, Dict
from qiskit_metal.qlibrary.core import BaseQubit
from shapely.geometry.base import CAP_STYLE


class TransmonPocketTeeth(BaseQubit):
    """Transmon pocket with 'Teeth' connection pads.

    Inherits `BaseQubit` class

    Description:
        Create a standard pocket transmon qubit for a ground plane with teeth
        Here we use the 'Teeth' shape which ones connected to the top pad and one connection pad.

    Options:
        Convention: Values (unless noted) are strings with units included,
        (e.g., '30um')

    Pocket:
        * pad_gap            - the distance between the two charge islands, which is also the
          resulting 'length' of the pseudo junction
        * inductor_width     - width of the pseudo junction between the two charge islands
          (if in doubt, make the same as pad_gap). Really just for simulating
          in HFSS / other EM software
        * pad_width          - the width (x-axis) of the charge island pads, except the circle radius from both sides
        * pad_height         - the size (y-axis) of the charge island pads
        * pocket_width       - size of the pocket (cut out in ground) along x-axis
        * pocket_height      - size of the pocket (cut out in ground) along y-axis
        * coupled_pad_gap    - the distance between the two teeth shape
        * coupled_pad_width  - the width (x-axis) of the teeth shape on the island pads
        * coupled_pad_height - the size (y-axis) of the teeth shape on the island pads
                            

    Connector lines:
        * pad_gap        - space between the connector pad and the charge island it is
          nearest to
        * pad_width      - width (x-axis) of the connector pad
        * pad_height     - height (y-axis) of the connector pad
        * pad_cpw_shift  - shift the connector pad cpw line by this much away from qubit
        * pad_cpw_extent - how long should the pad be - edge that is parallel to pocket
        * cpw_width      - center trace width of the CPW line
        * cpw_gap        - dielectric gap width of the CPW line
        * cpw_extend     - depth the connector line extends into ground (past the pocket edge)
        * pocket_extent  - How deep into the pocket should we penetrate with the cpw connector
          (into the ground plane)
        * pocket_rise    - How far up or down relative to the center of the transmon should we
          elevate the cpw connection point on the ground plane
        * loc_W / H      - which 'quadrant' of the pocket the connector is set to, +/- 1 (check
          if diagram is correct)


    Sketch:
        Below is a sketch of the qubit
        ::

                 +1              0             +1
                _________________________________
            -1  |                |               |  +1      Y
                |           | | |_| | |          |          ^
                |        ___| |_____| |____      |          |
                |       /     island       \     |          |----->  X
                |       \__________________/     |
                |                |               |
                |  pocket        x               |
                |        ________|_________      |
                |       /                  \     |
                |       \__________________/     |
                |                                |
                |                                |
            -1  |________________________________|   +1
                 
                 -1                            -1

    .. image::
        transmon_pocket_teeth.png

    .. meta::
        Transmon Pocket Teeth

    """

    #_img = 'transmon_pocket1.png'

    # Default drawing options
    default_options = Dict(
        pad_gap='30um',
        inductor_width='20um',
        pad_width='400um',
        pad_height='90um',
        pocket_width='650um',
        pocket_height='650um',
        # coupled_pad belongs to the teeth part. Teeth will have same height/width and are symmetric.
        coupled_pad_height='150um',
        coupled_pad_width='20um',
        coupled_pad_gap='50um',  # One can arrange the gap between the teeth.
        # orientation = 90 has dipole aligned along the +X axis, while 0 aligns to the +Y axis
        _default_connection_pads=Dict(
            pad_gap='15um',
            pad_width='20um',
            pad_height='150um',
            pad_cpw_shift='0um',
            pad_cpw_extent='25um',
            cpw_width='10um',
            cpw_gap='6um',
            # : cpw_extend: how far into the ground to extend the CPW line from the coupling pads
            cpw_extend='100um',
            pocket_extent='5um',
            pocket_rise='0um',
            loc_W='+1',  # width location  only +-1 or 0,
            loc_H='+1',  # height location  only +-1 or 0
        ))
    """Default drawing options"""

    component_metadata = Dict(short_name='Pocket',
                              _qgeometry_table_path='True',
                              _qgeometry_table_poly='True',
                              _qgeometry_table_junction='True')
    """Component metadata"""

    TOOLTIP = """Transmon pocket with teeth pads."""

    def make(self):
        """Define the way the options are turned into QGeometry.

        The make function implements the logic that creates the geoemtry
        (poly, path, etc.) from the qcomponent.options dictionary of
        parameters, and the adds them to the design, using
        qcomponent.add_qgeometry(...), adding in extra needed
        information, such as layer, subtract, etc.
        """
        self.make_pocket()
        self.make_connection_pads()

    def make_pocket(self):
        """Makes standard transmon in a pocket."""

        # self.p allows us to directly access parsed values (string -> numbers) form the user option
        p = self.p
        #  pcop = self.p.coupled_pads[name]  # parser on connector options

        # since we will reuse these options, parse them once and define them as variables
        pad_width = p.pad_width
        pad_height = p.pad_height
        pad_gap = p.pad_gap
        coupled_pad_height = p.coupled_pad_height
        coupled_pad_width = p.coupled_pad_width
        coupled_pad_gap = p.coupled_pad_gap

        # make the pads as rectangles (shapely polygons)
        pad = draw.rectangle(pad_width, pad_height)

        pad_top = draw.translate(pad, 0, +(pad_height + pad_gap) / 2.)
        # Here, you make your pads round. Not sharp shape on the left and right sides and also this should be the same for the bottom pad as the top pad.
        circ_left_top = draw.Point(-pad_width / 2., +(pad_height + pad_gap) /
                                   2.).buffer(pad_height / 2,
                                              resolution=16,
                                              cap_style=CAP_STYLE.round)
        circ_right_top = draw.Point(pad_width / 2., +(pad_height + pad_gap) /
                                    2.).buffer(pad_height / 2,
                                               resolution=16,
                                               cap_style=CAP_STYLE.round)
        # In here you create the teeth part and then you union them as one with the pad. Teeth only belong to top pad.
        coupled_pad = draw.rectangle(coupled_pad_width,
                                     coupled_pad_height + pad_height)
        coupler_pad_round = draw.Point(0., (coupled_pad_height + pad_height) /
                                       2).buffer(coupled_pad_width / 2,
                                                 resolution=16,
                                                 cap_style=CAP_STYLE.round)
        coupled_pad = draw.union(coupled_pad, coupler_pad_round)
        coupled_pad_left = draw.translate(
            coupled_pad, -(coupled_pad_width / 2. + coupled_pad_gap / 2.),
            +coupled_pad_height / 2. + pad_height + pad_gap / 2. -
            pad_height / 2)
        coupled_pad_right = draw.translate(
            coupled_pad, (coupled_pad_width / 2. + coupled_pad_gap / 2.),
            +coupled_pad_height / 2. + pad_height + pad_gap / 2. -
            pad_height / 2)
        pad_top_tmp = draw.union([circ_left_top, pad_top, circ_right_top])
        # The coupler pads are only created if low_W=0 and low_H=+1
        for name in self.options.connection_pads:
            if self.options.connection_pads[name][
                    'loc_W'] == 0 and self.options.connection_pads[name][
                        'loc_H'] == +1:
                pad_top_tmp = draw.union([
                    circ_left_top, coupled_pad_left, pad_top, coupled_pad_right,
                    circ_right_top
                ])
        pad_top = pad_top_tmp
        # Round part for the bottom pad. And again you should unite all of them.
        pad_bot = draw.translate(pad, 0, -(pad_height + pad_gap) / 2.)
        circ_left_bot = draw.Point(-pad_width / 2, -(pad_height + pad_gap) /
                                   2.).buffer(pad_height / 2,
                                              resolution=16,
                                              cap_style=CAP_STYLE.round)
        circ_right_bot = draw.Point(pad_width / 2, -(pad_height + pad_gap) /
                                    2.).buffer(pad_height / 2,
                                               resolution=16,
                                               cap_style=CAP_STYLE.round)
        pad_bot = draw.union([pad_bot, circ_left_bot, circ_right_bot])

        rect_jj = draw.LineString([(0, -pad_gap / 2), (0, +pad_gap / 2)])
        # the draw.rectangle representing the josephson junction
        # rect_jj = draw.rectangle(p.inductor_width, pad_gap)

        rect_pk = draw.rectangle(p.pocket_width, p.pocket_height)

        # Rotate and translate all qgeometry as needed.
        # Done with utility functions in Metal 'draw_utility' for easy rotation/translation
        # NOTE: Should modify so rotate/translate accepts qgeometry, would allow for
        # smoother implementation.
        polys = [rect_jj, pad_top, pad_bot, rect_pk]
        polys = draw.rotate(polys, p.orientation, origin=(0, 0))
        polys = draw.translate(polys, p.pos_x, p.pos_y)
        [rect_jj, pad_top, pad_bot, rect_pk] = polys

        # Use the geometry to create Metal qgeometry
        self.add_qgeometry('poly', dict(pad_top=pad_top, pad_bot=pad_bot))
        self.add_qgeometry('poly', dict(rect_pk=rect_pk), subtract=True)
        # self.add_qgeometry('poly', dict(
        #     rect_jj=rect_jj), helper=True)
        self.add_qgeometry('junction',
                           dict(rect_jj=rect_jj),
                           width=p.inductor_width)

    def make_connection_pads(self):
        """Makes standard transmon in a pocket."""
        for name in self.options.connection_pads:
            self.make_connection_pad(name)

    def make_connection_pad(self, name: str):
        """Makes n individual connector.

        Args:
            name (str) : Name of the connector
        """

        # self.p allows us to directly access parsed values (string -> numbers) form the user option
        p = self.p
        pc = self.p.connection_pads[name]  # parser on connector options

        # define commonly used variables once
        cpw_width = pc.cpw_width
        cpw_extend = pc.cpw_extend
        pad_width = pc.pad_width
        pad_height = pc.pad_height
        pad_cpw_shift = pc.pad_cpw_shift
        pocket_rise = pc.pocket_rise
        pocket_extent = pc.pocket_extent

        loc_W = float(pc.loc_W)
        loc_W, loc_H = float(pc.loc_W), float(pc.loc_H)
        if float(loc_W) not in [-1., +1., 0] or float(loc_H) not in [-1., +1.]:
            self.logger.info(
                'Warning: Did you mean to define a transmon qubit with loc_W and'
                ' loc_H that are not +1, -1, or 0? Are you sure you want to do this?'
            )

        # Define the geometry
        # Connector pad

        if float(loc_W) != 0:
            connector_pad = draw.rectangle(pad_width, pad_height,
                                           -pad_width / 2, pad_height / 2)
            # Connector CPW wire
            connector_wire_path = draw.wkt.loads(f"""LINESTRING (\
                0 {pad_cpw_shift+cpw_width/2}, \
                {pc.pad_cpw_extent}                           {pad_cpw_shift+cpw_width/2}, \
                {(p.pocket_width-p.pad_width)/2-pocket_extent} {pad_cpw_shift+cpw_width/2+pocket_rise}, \
                {(p.pocket_width-p.pad_width)/2+cpw_extend}    {pad_cpw_shift+cpw_width/2+pocket_rise}\
                                            )""")
        else:
            connector_pad = draw.rectangle(pad_width, pad_height, 0,
                                           pad_height / 2)
            connector_wire_path = draw.LineString(
                [[0, pad_height],
                 [
                     0,
                     (p.pocket_width / 2 - p.pad_height - p.pad_gap / 2 -
                      pc.pad_gap) + cpw_extend
                 ]])

        # Position the connector, rotate and translate
        objects = [connector_pad, connector_wire_path]

        if loc_W == 0:
            loc_Woff = 1
        else:
            loc_Woff = loc_W

        objects = draw.scale(objects, loc_Woff, loc_H, origin=(0, 0))
        objects = draw.translate(
            objects,
            loc_W * (p.pad_width) / 2.,
            loc_H * (p.pad_height + p.pad_gap / 2 + pc.pad_gap))
        objects = draw.rotate_position(objects, p.orientation,
                                       [p.pos_x, p.pos_y])
        [connector_pad, connector_wire_path] = objects

        self.add_qgeometry('poly', {f'{name}_connector_pad': connector_pad})
        self.add_qgeometry('path', {f'{name}_wire': connector_wire_path},
                           width=cpw_width)
        self.add_qgeometry('path', {f'{name}_wire_sub': connector_wire_path},
                           width=cpw_width + 2 * pc.cpw_gap,
                           subtract=True)

        ############################################################

        # add pins
        points = np.array(connector_wire_path.coords)
        self.add_pin(name,
                     points=points[-2:],
                     width=cpw_width,
                     input_as_norm=True)
