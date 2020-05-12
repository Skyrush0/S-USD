from pxr import UsdGeom, Gf


# --------------------USD specific----------------------------
def add_stage_metadata(stage, params):
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.y)
    if params["animation"] is not None:
        stage.SetStartTimeCode(params["animation"][0])
        stage.SetEndTimeCode(params["animation"][1])


def build_transform(obj, frame=None):
    tfm_matrix = obj.Kinematics.Local.Transform.Matrix4 if frame is None else obj.Kinematics.Local.GetTransform2(frame).Matrix4
    return Gf.Matrix4d(
            tfm_matrix.Value(0, 0), tfm_matrix.Value(0, 1), tfm_matrix.Value(0, 2), tfm_matrix.Value(0, 3),
            tfm_matrix.Value(1, 0), tfm_matrix.Value(1, 1), tfm_matrix.Value(1, 2), tfm_matrix.Value(1, 3),
            tfm_matrix.Value(2, 0), tfm_matrix.Value(2, 1), tfm_matrix.Value(2, 2), tfm_matrix.Value(2, 3),
            tfm_matrix.Value(3, 0), tfm_matrix.Value(3, 1), tfm_matrix.Value(3, 2), tfm_matrix.Value(3, 3),
        )


# --------------------XSI specific----------------------------
def is_stands(pc_object):
    pc_geo = pc_object.GetActivePrimitive2().Geometry
    strands_position_attr = pc_geo.GetICEAttributeFromName("StrandPosition")
    strands_data = strands_position_attr.DataArray2D
    return len(strands_data) > 0


def is_constant_topology(mesh, opt_anim):
    if opt_anim is None:
        return True
    else:
        # get number of points at the first frame
        geo = mesh.GetActivePrimitive3(opt_anim[0]).GetGeometry3(opt_anim[0])
        vertex_count = len(geo.Vertices)
        # next iterate by other frames
        for frame in range(opt_anim[0] + 1, opt_anim[1] + 1):
            geo_frame = mesh.GetActivePrimitive3(frame).GetGeometry3(frame)
            verts_frame = len(geo_frame.Vertices)
            if vertex_count != verts_frame:
                return False
        return True


def vector_to_tuple(vector):
    return (vector.X, vector.Y, vector.Z)


# --------------------General----------------------------
def get_last_folder(path):
    parts = path.split("\\")
    return parts[-2]


def get_bounding_box(positions):
    if len(positions) == 0:
        return [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0)]

    min_x = positions[0][0]
    min_y = positions[0][1]
    min_z = positions[0][2]
    max_x = positions[0][0]
    max_y = positions[0][1]
    max_z = positions[0][2]
    for p in positions:
        if p[0] < min_x:
            min_x = p[0]
        elif p[0] > max_x:
            max_x = p[0]
        if p[1] < min_y:
            min_y = p[1]
        elif p[1] > max_y:
            max_y = p[1]
        if p[2] < min_z:
            min_z = p[2]
        elif p[2] > max_z:
            max_z = p[2]
    return [(min_x, min_y, min_z), (max_x, max_y, max_z)]


def get_index_in_array(array, value):  # also for tuple
    for a_index in range(len(array)):
        if array[a_index] == value:
            return a_index
    return None
