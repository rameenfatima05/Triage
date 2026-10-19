"""Topics that exist in the NEW 2023 Punjab Class 9 book but have no history in the 2015-2024 papers.
Same tuple shape as taxonomy.TOPICS: (display name, chapter label, hours a student needs). Hours are estimates - edit freely.
The model never predicts these from old papers. They stay category 'new' until an uploaded paper contains them."""
NEW_TOPICS = {
 'sets_basic':('Sets: definitions & notation', 'Sets & functions', 1.0),
 'sets_venn':('Venn diagrams & set operations', 'Sets & functions', 1.5),
 'relations':('Binary relations', 'Sets & functions', 1.0),
 'functions_notation':('Functions: notation, linear & quadratic', 'Sets & functions', 1.5),
 'trig_measure':('Angle measure: degrees & radians', 'Trigonometry', 1.0),
 'trig_ratios':('Trigonometric ratios', 'Trigonometry', 1.5),
 'trig_identities':('Trigonometric identities', 'Trigonometry', 1.5),
 'trig_special':('Ratios of special angles', 'Trigonometry', 1.0),
 'trig_solve':('Solving right triangles', 'Trigonometry', 1.5),
 'trig_elevation':('Angles of elevation & depression', 'Trigonometry', 1.5),
 'logic_statements':('Statements & logical operators', 'Logic', 1.0),
 'logic_proof':('Deductive proof, theorem & axiom', 'Logic', 1.5),
 'graph_exp':('Exponential graphs, growth & decay', 'Graphs & coordinates', 1.0),
 'stat_tables':('Frequency tables (grouped data)', 'Information handling', 1.0),
 'stat_graphs':('Histograms & frequency polygons', 'Information handling', 1.5),
 'stat_central':('Mean, median, weighted mean', 'Information handling', 1.5),
 'prob_single':('Probability of a single event', 'Probability', 1.0),
 'prob_relfreq':('Relative frequency', 'Probability', 0.7),
 'prob_expected':('Expected frequency', 'Probability', 0.7),
 'feasible_region':('Feasible region & max/min values', 'Equations & inequalities', 1.5),
}
