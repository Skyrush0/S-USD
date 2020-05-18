from pxr import UsdGeom, Gf
import os


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


def is_contains_transform(usd_prim):
    usd_props = usd_prim.GetPropertyNames()
    return "xformOp:transform" in usd_props


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


def is_materials_equals(mat_a, mat_b):
    return mat_a.Name == mat_b.Name and mat_a.Library.Name == mat_b.Library.Name


def buil_material_name(material):
    return material.Library.Name + "_" + material.Name


def build_material_identifier(material):
    return (material.Library.Name, material.Name)


def build_export_object_caption(obj, frame=None):
    return "Export object " + obj.Name + (" (frame " + str(frame) + ")" if frame is not None else "")


def set_xsi_transform_at_frame(app, xsi_object, usd_tfm, frame=None):
    # set tfm matrix
    tfm_matrix = xsi_object.Kinematics.Local.Transform.Matrix4
    row_00 = usd_tfm.GetRow(0)
    row_01 = usd_tfm.GetRow(1)
    row_02 = usd_tfm.GetRow(2)
    row_03 = usd_tfm.GetRow(3)
    tfm_matrix.Set(row_00[0], row_00[1], row_00[2], row_00[3],
                   row_01[0], row_01[1], row_01[2], row_01[3],
                   row_02[0], row_02[1], row_02[2], row_02[3],
                   row_03[0], row_03[1], row_03[2], row_03[3])
    # form transform
    new_transfrom = xsi_object.Kinematics.Local.Transform
    new_transfrom.SetMatrix4(tfm_matrix)
    # apply transform
    xsi_object.Kinematics.Local.Transform = new_transfrom
    if frame is not None:
        xsi_translation = new_transfrom.Translation
        xsi_rotation = new_transfrom.Rotation.XYZAngles
        xsi_scale = new_transfrom.Scaling
        # set keys
        app.SaveKey(xsi_object.Name + ".kine.local.posx", frame, xsi_translation.X)
        app.SaveKey(xsi_object.Name + ".kine.local.posy", frame, xsi_translation.Y)
        app.SaveKey(xsi_object.Name + ".kine.local.posz", frame, xsi_translation.Z)
        app.SaveKey(xsi_object.Name + ".kine.local.rotx", frame, xsi_rotation.X * 180.0 / 3.14)
        app.SaveKey(xsi_object.Name + ".kine.local.roty", frame, xsi_rotation.Y * 180.0 / 3.14)
        app.SaveKey(xsi_object.Name + ".kine.local.rotz", frame, xsi_rotation.Z * 180.0 / 3.14)
        app.SaveKey(xsi_object.Name + ".kine.local.sclx", frame, xsi_scale.X)
        app.SaveKey(xsi_object.Name + ".kine.local.scly", frame, xsi_scale.Y)
        app.SaveKey(xsi_object.Name + ".kine.local.sclz", frame, xsi_scale.Z)


def set_xsi_transform(app, xsi_obj, usd_tfm):
    tfm_data = usd_tfm[0]
    time_samples = usd_tfm[1]
    if len(time_samples) == 0:
        # no animation
        set_xsi_transform_at_frame(app, xsi_obj, tfm_data)
    else:
        for i in range(len(time_samples)):
            frame = time_samples[i]
            set_xsi_transform_at_frame(app, xsi_obj, tfm_data[i], frame=frame)


def set_xsi_visibility(xsi_obj, is_visible):
    # in Softimage visibility is not inherited from parent objects. SO, in our case "inherited" means visible
    vis_prop = xsi_obj.Properties("Visibility")
    vis_prop.Parameters("viewvis").Value = is_visible
    vis_prop.Parameters("rendvis").Value = is_visible


# --------------------General----------------------------
def from_scene_path_to_models_path(path):
    path_head, path_tail = os.path.split(path)
    # change last folder from Scene to Models
    folders = path_head.split("\\")
    models_path = "\\".join(folders[:-1]) + "\\Models\\"
    # change extension in the file name
    name_parts = path_tail.split(".")
    file_name = ".".join(name_parts[:-1]) + ".usda"
    return models_path + file_name


def get_last_folder(path):
    parts = path.split("\\")
    return parts[-2]


def get_file_extension(path):
    return path.split(".")[-1]


def get_file_name(full_name):
    parts = full_name.split(".")
    return ".".join(parts[:-1])


def remove_first_folder(path):
    '''transform the path a/b/c/d to a/c/d
    '''
    parts = path.split("/")
    return "/".join([parts[0]] + parts[2:])


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


def get_extension_from_params(params):
    opts = params.get("options", None)
    if opts is None:
        return "usd"
    else:
        return opts.get("extension", "usd")


def verify_extension(file_path):
    path_head, path_tail = os.path.split(file_path)
    point_index = path_tail.rfind(".")
    if point_index < 0:
        return file_path + ".usda"
    else:
        file_ext = path_tail[point_index + 1:]
        if file_ext in ["usd", "usda", "usdz"]:
            return file_path
        else:
            return path_head + "\\" + path_tail[:point_index] + ".usda"


def transform_path_to_relative(path, base_path):
    '''transform absolute path to relative with respect to base_path
    '''
    return os.path.relpath(base_path, path)[3:]
