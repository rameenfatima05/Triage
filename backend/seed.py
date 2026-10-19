"""Hand-transcribed topic labels from the Rawalpindi Class 9 papers we have (Group I 2015/16/18/19/23/24 + Group II 2024).
Lets the whole pipeline run with no API key. extract.py produces the same structure from real scans."""
import json
P = [
(2015,1,"ineq_solve coord_pair mat_det cplx_i_power log_def surd_conj factor_quad sqrt_factor area_defs parallelogram_props tri_types tri_angle_sum parallelogram_props geo_symbols ratio_prop_def",
 ["mat_types mat_ops exp_simplify cplx_ops log_solve rational_expr sci_notation factor_cubes factor_thm","sqrt_factor radical_eq abs_eq coord_defs mx_c distance midpoint parallelogram_def congruent_defs","bisector_defs triangle_inequality congruent_defs bisector_defs pythagoras pythagoras area_defs concurrency_defs constr_triangle"],
 "mat_solve exp_simplify log_table rational_expr factor_thm rational_expr linear_eq constr_triangle"),
(2016,1,"perfect_square_k hcf_lcm ineq_solve coord_quadrant mat_ops cplx_ops log_laws surd_conj bisector_defs ratio_prop_def area_defs tri_types distance tri_angle_sum parallelogram_props",
 ["mat_types mat_ops real_prop cplx_ops log_def log_solve surd_conj rational_expr factor_quad","hcf_lcm linear_eq radical_eq coord_defs mx_c distance tri_types congruent_defs concurrency_defs","bisector_defs pythagoras congruent_defs proportional_sides pythagoras pythagoras constr_basic parallelogram_def constr_triangle"],
 "mat_solve exp_simplify log_table alg_identity factor_thm hcf_lcm abs_eq constr_triangle"),
(2018,1,"tri_types geo_basic parallelogram_def bisector_defs geo_basic area_defs concurrency_defs mat_types exp_simplify log_def surd_conj factor_quad hcf_lcm ineq_solve coord_quadrant",
 ["mat_types mat_ops exp_simplify cplx_ops log_solve sci_notation rational_expr surd_conj factor_quad","hcf_lcm radical_eq abs_eq coord_defs graph_plot distance midpoint congruent_defs tri_angle_sum","bisector_defs tri_types ratio_prop_def proportional_sides ratio_prop_def parallelogram_def concurrency_defs pythagoras constr_triangle"],
 "mat_solve exp_simplify log_table alg_identity factor_cubes sqrt_division linear_eq constr_triangle"),
(2019,1,"mat_order real_prop log_def surd_conj factor_quad hcf_lcm ineq_solve coord_quadrant midpoint tri_angle_sum concurrency_defs bisector_defs congruent_defs area_defs tri_types",
 ["mat_types mat_ops real_prop real_prop log_def log_solve rational_expr alg_identity factor_quad","sqrt_factor radical_eq abs_eq mx_c coord_defs distance midpoint congruent_defs parallelogram_def","bisector_defs triangle_inequality proportional_sides pythagoras pythagoras area_defs area_defs constr_triangle concurrency_defs"],
 "mat_solve exp_simplify log_table alg_identity factor_thm hcf_lcm radical_eq constr_triangle"),
(2023,1,"ineq_solve coord_pair distance congruent_defs parallelogram_props bisector_defs congruent_defs area_defs concurrency_defs mat_types cplx_i_power log_def surd_conj factor_quad hcf_lcm",
 ["mat_types mat_ops cplx_ops exp_simplify sci_notation log_solve rational_expr exp_simplify factor_quad","sqrt_factor radical_eq abs_eq mx_c graph_plot tri_types midpoint congruent_defs parallelogram_props","bisector_defs triangle_inequality ratio_prop_def proportional_sides pythagoras pythagoras area_defs concurrency_defs constr_triangle"],
 "mat_ops exp_simplify log_table alg_identity factor_thm sqrt_division ineq_solve constr_triangle"),
(2024,1,"mat_types radical_form log_def factor_cubes factor_quad hcf_lcm ineq_solve coord_pair distance tri_types parallelogram_props geo_symbols congruent_defs concurrency_defs bisector_defs",
 ["mat_det exp_simplify cplx_ops log_laws log_def surd_conj surd_conj factor_quad factor_cubes","hcf_lcm abs_eq ineq_solve mx_c coord_defs distance midpoint congruent_defs parallelogram_def","bisector_defs triangle_inequality proportional_sides pythagoras pythagoras area_defs area_defs concurrency_defs constr_triangle"],
 "mat_solve exp_simplify log_table alg_identity factor_thm perfect_square_k linear_eq constr_triangle"),
(2024,2,"perfect_square_k sqrt_factor ineq_solve mx_c tri_types congruent_defs parallelogram_props geo_basic geo_basic concurrency_defs tri_types mat_order exp_simplify log_def surd_conj",
 ["mat_ops real_prop exp_simplify log_solve log_laws alg_identity surd_conj factor_quad factor_thm","hcf_lcm abs_eq linear_eq graph_plot mx_c distance midpoint congruent_defs parallelogram_def","bisector_defs triangle_inequality ratio_prop_def pythagoras pythagoras area_defs area_defs concurrency_defs constr_triangle"],
 "mat_solve exp_simplify log_table alg_identity factor_quad perfect_square_k linear_eq constr_triangle"),
]
M = {"o":1,"s":2,"l":4,"p":8}
def build():
    out = []
    for y,g,o,s,l in P:
        it = [dict(slot="o",q=f"1.{i+1}",topic=t,marks=1) for i,t in enumerate(o.split())]
        for qi,row in enumerate(s):
            it += [dict(slot="s",q=str(qi+2),topic=t,marks=2) for t in row.split()]
        it += [dict(slot="l",q=f"5-8.{i+1}",topic=t,marks=4) for i,t in enumerate(l.split())]
        it.append(dict(slot="p",q="9",topic="thm_bisect_or_area",marks=8))
        out.append(dict(year=y,group=g,items=it,source="manual_seed"))
    return out
if __name__ == "__main__":
    json.dump(build(), open("data/papers.json","w"), indent=1); print("papers:", len(P))
