import numpy as np
import pulp


def solve_pairing_LP_problem(similarity_matrix):
    """

    :param similarity_matrix: np matrix of shape (nbr_dut_shapes, nbr_gt_shapes)
    :return:
    """
    nbr_shapes, nbr_shapes_gt = similarity_matrix.shape
    cij_variables = list()
    for i in range(nbr_shapes):
        ci_list = list()
        for j in range(nbr_shapes_gt):
            cij_var = pulp.LpVariable('c_{%i,%i}' % (i, j), 0, 1, pulp.LpInteger)
            ci_list.append(cij_var)
        cij_variables.append(ci_list)

    cij_variables = np.array(cij_variables)

    # Formulate optimization problem
    prob = pulp.LpProblem("Box pairing", pulp.LpMaximize)

    prob += np.sum(cij_variables * similarity_matrix), 'objective function'

    # An annotation object can only be assigned to one correction object
    for i in range(nbr_shapes):
        prob += np.sum(cij_variables[i, :]) <= 1

    for j in range(nbr_shapes_gt):
        prob += np.sum(cij_variables[:, j]) <= 1

    prob.solve()

    # map matrix from pulp variables to solution values
    cij_matrix_result = [[cij_variables[i, j].varValue for j in range(nbr_shapes_gt)] for i in range(nbr_shapes)]
    cij_matrix_result = np.array(cij_matrix_result).astype(int)
    return cij_matrix_result


def solve_pairing_LP_problem_with_obj(anno, corr, calculate_similarity_matrix):
    """

    :param anno:
    :param corr:
    :param calculate_similarity_matrix: A callback function that calculates a similarity matrix (gamma) for two
                                        annotations, where gamma_i,j in [theta, 1] U {-1} where theta > 0 and denotes
                                        the threshold where two boxes for examples is considered as possible pairings

    :return:
    """

    nbr_anno_obj = len(anno.data_content)
    nbr_corr_obj = len(corr.data_content)

    # Define the pairing matrix C, c_i,j = 1 implies that obj i is paired with obj j
    cij_matrix = list()
    for i_anno_obj in range(nbr_anno_obj):
        c_i_list = list()
        for i_corr_obj in range(nbr_corr_obj):
            tmp_cij = pulp.LpVariable('c_{%i,%i}' % (i_anno_obj, i_corr_obj), 0, 1, pulp.LpInteger)
            c_i_list.append(tmp_cij)
        cij_matrix.append(c_i_list)
    cij_matrix = np.array(cij_matrix)

    # define similarity matrix
    gamma_matrix = calculate_similarity_matrix(anno, corr)

    # Formulate optimization problem
    prob = pulp.LpProblem("Box pairing", pulp.LpMaximize)

    prob += np.sum(cij_matrix * gamma_matrix), 'objective function'

    # An annotation object can only be assigned to one correction object
    for i in range(nbr_anno_obj):
        prob += np.sum(cij_matrix[i, :]) <= 1

    for j in range(nbr_corr_obj):
        prob += np.sum(cij_matrix[:, j]) <= 1

    prob.solve()

    # map matrix from pulp variables to solution values
    cij_matrix_result = [[cij_matrix[i, j].varValue for j in range(nbr_corr_obj)] for i in range(nbr_anno_obj)]
    cij_matrix_result = np.array(cij_matrix_result).astype(int)
    return cij_matrix_result


def match_annotations(anno, corr, calculate_similarity_matrix):
    if len(anno.data_content) == 0 and len(corr.data_content) == 0:
        return [], [], []
    elif len(anno.data_content) == 0:
        return [], [], corr.data_content
    elif len(corr.data_content) == 0:
        return [], anno.data_content, []

    assert len(anno.data_content) != 0
    assert len(corr.data_content) != 0

    cij_matrix_result = solve_pairing_LP_problem_with_obj(anno, corr, calculate_similarity_matrix)

    # create lists for paired and unpaired objects
    anno_obj_with_no_match = list()
    matching_obj_pair_list = list()
    for i_anno_obj, anno_obj in enumerate(anno.data_content):
        if np.sum(cij_matrix_result[i_anno_obj, :]) > 0:  # anno obj is paired with a corr obj
            corr_obj_ix = np.argmax(cij_matrix_result[i_anno_obj, :])
            corr_obj = corr.data_content[corr_obj_ix]
            matching_obj_pair_list.append((anno_obj, corr_obj))
        else:  # anno cannot be paired with an correction
            anno_obj_with_no_match.append(anno_obj)

    corr_obj_with_no_match = list()
    for i_corr_obj, corr_obj in enumerate(corr.data_content):
        if np.sum(cij_matrix_result[:, i_corr_obj]) == 0:  # correction cannot be paired with an annotation
            corr_obj_with_no_match.append(corr_obj)

    return matching_obj_pair_list, anno_obj_with_no_match, corr_obj_with_no_match
