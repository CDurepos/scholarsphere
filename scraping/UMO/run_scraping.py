from scraping.UMO.parsers.biography_compilers import B1Compiler, B2Compiler, B3Compiler, B4Compiler, B5Compiler

bc1 = B1Compiler()
bc2 = B2Compiler()
bc3 = B3Compiler()
bc4 = B4Compiler()
bc5 = B5Compiler()

bc1.collect()
bc2.collect()
bc3.collect()
bc4.collect()
bc5.collect()