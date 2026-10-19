"""Maps each exam topic to the NEW 2023 Punjab Class 9 textbook (unit, section, exercise, printed page).
Found by OCR of the book's contents page, section headings and exercise banners.
status: 'found'   = section located in the book
        'partial' = related material exists but not an exact match (check the page)
        'absent'  = no section found in the new book -> likely removed by the syllabus change
Exercise numbers come from OCR of banners; entries marked verify=True should be eyeballed once."""
UNITS = {1:("Real Numbers",1),2:("Logarithms",21),3:("Set and Functions",37),4:("Factorization and Algebraic Manipulation",65),
 5:("Linear Equations and Inequalities",82),6:("Trigonometry",97),7:("Coordinate Geometry",123),8:("Logic",147),
 9:("Similar Figures",161),10:("Graphs of Functions",185),11:("Loci and Construction",200),12:("Information Handling",215),13:("Probability",243)}
def B(u,sec,ex,pg,status="found",verify=False): return dict(unit=u,unit_name=UNITS[u][0],section=sec,exercise=ex,page=pg,status=status,verify=verify)
ABSENT = dict(unit=None,unit_name=None,section=None,exercise=None,page=None,status="absent",verify=False)
BOOK = {
 "real_prop":B(1,"1.1 Introduction to Real Numbers","1.1",10),
 "exp_simplify":B(1,"1.2.1 Laws of Radicals and Indices","1.2",13),
 "radical_form":B(1,"1.2.1 Laws of Radicals and Indices","1.2",13),
 "surd_conj":B(1,"1.2.2 Surds and their Applications","1.2",13),
 "sci_notation":B(2,"2.1 Scientific Notation","2.1",22),
 "log_def":B(2,"2.2.1 Logarithm of a Real Number","2.2",24),
 "log_table":B(2,"2.3 Common Logarithm (tables)","2.3",30),
 "log_laws":B(2,"2.4 Laws of Logarithm","2.4",34),
 "log_solve":B(2,"2.4.1 Applications of Logarithm","2.4",34),
 "factor_quad":B(4,"4.1.2 Trinomial Factoring","4.1",69),
 "factor_cubes":B(4,"4.1.3 Factorizing Quadratic and Algebraic Expressions","4.1",69,verify=True),
 "alg_identity":B(4,"Unit 4, algebraic manipulation","4.2",73,"partial",True),
 "rational_expr":B(4,"Unit 4, algebraic manipulation","4.2",73,"partial",True),
 "hcf_lcm":B(4,"4.3 HCF and LCM","4.3",77),
 "sqrt_factor":B(4,"4.4 Square Root of an Algebraic Expression","4.4",80,verify=True),
 "sqrt_division":B(4,"4.4 Square Root of an Algebraic Expression","4.4",80,"partial",True),
 "linear_eq":B(5,"5.1.1 Solving a Linear Equation in One Variable","5.1",90),
 "ineq_solve":B(5,"5.2 Linear Inequalities","5.1",90,verify=True),
 "coord_defs":B(7,"7.1 Coordinate Plane","7.1",126),
 "coord_quadrant":B(7,"7.1 Coordinate Plane","7.1",126),
 "coord_pair":B(7,"7.1 Coordinate Plane","7.1",126),
 "distance":B(7,"7.1.1 The Distance Formula","7.1",126),
 "midpoint":B(7,"7.1.2 Mid Point Formula","7.1",126),
 "mx_c":B(7,"7.2 Equation of a Straight Line","7.2",None,verify=True),
 "graph_plot":B(10,"10.1 Functions and their Graphs","10.1",183),
 "pythagoras":B(6,"6.x Trigonometry (Pythagoras used in ratios/triangle solving)","6.5",115,"partial",True),
 "constr_triangle":B(11,"11.1 Construction of Triangles","11.1",198),
 "constr_basic":B(11,"11.2-11.3 Perpendicular and Angle Bisectors","11.1",198,"partial",True),
 "bisector_defs":B(11,"11.2-11.3 Perpendicular and Angle Bisectors","11.1",198,"partial",True),
 "concurrency_defs":B(11,"11.2 Perpendicular Bisectors and Medians of a Triangle","11.1",198,"partial",True),
 "thm_bisect_or_area":B(11,"11.2 right bisectors (equal-area theorem not found)","11.1",198,"partial",True),
 "parallelogram_def":B(9,"9.4 Geometrical Properties of Polygons","9.3",173,"partial",True),
 "parallelogram_props":B(9,"9.4 Geometrical Properties of Polygons","9.3",173,"partial",True),
 "proportional_sides":B(9,"9.1 Similarity of Polygons","9.1",162,"partial",True),
 "ratio_prop_def":B(9,"9.1 Similarity of Polygons","9.1",162,"partial",True),
 "congruent_defs":B(9,"9.1.1 Identification of Similar Triangles","9.1",162,"partial",True),
}
# nothing found for these in the contents, headings or keyword search of the new book
for t in ["mat_order","mat_types","mat_ops","mat_det","mat_solve","cplx_i_power","cplx_ops","factor_thm","perfect_square_k",
          "abs_eq","radical_eq","tri_types","tri_angle_sum","triangle_inequality","area_defs","geo_basic","geo_symbols"]:
    BOOK[t] = dict(ABSENT)
def book_for(tid): return BOOK.get(tid, dict(ABSENT))

# --- NEW-syllabus-only topics (no past-paper history). Exercise numbers from OCR banners; verify=True where unsure. ---
BOOK.update({
 "sets_basic":B(3,"3.1 Mathematics as the Study of Patterns / Basic Definitions","3.1",None,verify=True),
 "sets_venn":B(3,"3.2.1 Identification of Sets Using Venn Diagram","3.2",53),
 "relations":B(3,"3.3 Binary Relations","3.3",61,verify=True),
 "functions_notation":B(3,"3.3.3-3.3.4 Function Notation, Linear and Quadratic Functions","3.3",61,verify=True),
 "trig_measure":B(6,"6.1 Angle Measurement (degrees, radians)","6.1",None,verify=True),
 "trig_ratios":B(6,"6.2 Trigonometric Ratios","6.2",105,verify=True),
 "trig_identities":B(6,"6.3 Trigonometric Identities","6.3",109,verify=True),
 "trig_special":B(6,"6.4 Ratios of Special Angles","6.4",112),
 "trig_solve":B(6,"6.5 Solution of a Triangle","6.5",115,verify=True),
 "trig_elevation":B(6,"6.6 Angles of Elevation and Depression","6.6",119,verify=True),
 "logic_statements":B(8,"8.1 Statement / Logical Operators","8.1",149,verify=True),
 "logic_proof":B(8,"8.1.4-8.1.5 Theorem, Axiom, Deductive Proof","8.2",None,verify=True),
 "graph_exp":B(10,"10.1.5 / 10.2 Exponential Functions, Growth and Decay","10.2",188,verify=True),
 "stat_tables":B(12,"12.1 Ungrouped and Grouped Data, Frequency Distribution","12.1",None,verify=True),
 "stat_graphs":B(12,"12.1.3-12.1.4 Histogram, Frequency Polygon","12.1",None,verify=True),
 "stat_central":B(12,"12.2 Measures of Location (mean, median, weighted mean)","12.2",None,verify=True),
 "prob_single":B(13,"13.1 Probability of a Single Event","13.1",242,verify=True),
 "prob_relfreq":B(13,"13.4 Relative Frequency","13.2",247,verify=True),
 "prob_expected":B(13,"13.6 Expected Frequency","13.2",247,verify=True),
 "feasible_region":B(5,"5.3 Feasible Solution, Maximum/Minimum Values","5.2",94,verify=True),
})
