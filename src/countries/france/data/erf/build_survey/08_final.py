# -*- coding:utf-8 -*-
# Created on 21 mai 2013
# This file is part of OpenFisca.
# OpenFisca is a socio-fiscal microsimulation software
# Copyright ©2013 Clément Schaff, Mahdi Ben Jelloul
# Licensed under the terms of the GVPLv3 or later license
# (see openfisca/__init__.py for details)

from __future__ import division
from numpy import where, NaN, random, logical_or as or_ 
from src.countries.france.data.erf.build_survey import show_temp, load_temp, save_temp
from src.countries.france.data.erf.build_survey.utilitaries import print_id, control
from numpy import logical_and as and_
from pandas import read_csv, HDFStore
import os

def final(year=2006):

##***********************************************************************/
    print('08_final: derniers réglages')
##***********************************************************************/

    # On définit comme célibataires les individus dont on n'a pas retrouvé la déclaration
    import gc
    gc.collect()
    final = load_temp("final", year=year)
    final.statmarit = where(final.statmarit.isnull(), 2, final.statmarit)

#START REMOVE 
# # recode quifoy # TODO: should have been done directly above
# table(final$quifoy, useNA="ifany")
# levels(final$quifoy) <- list("0"='vous', 
#                              "1"='conj',
#                              "2"='pac1',
#                              "3"='pac2',
#                              "4"='pac3',
#                              "5"='pac4',
#                              "6"='pac5',
#                              "7"='pac6',
#                              "8"='pac7',
#                              "9"='pac8')
# 
# final$quifoy <- as.numeric(levels(final$quifoy)[final$quifoy])
# 
# # recode quimen # TODO: should have been done directly above
# table(final$quimen, useNA="ifany")
# levels(final$quimen) <- list("0"="0", 
#                              "1"="1",
#                              "2"='enf1',
#                              "3"='enf2',
#                              "4"='enf3',
#                              "5"='enf4',
#                              "6"='enf5',
#                              "7"='enf6',
#                              "8"='enf7',
#                              "9"='enf8',
#                              "10"='enf9')
# str(final$quimen)
# final$quimen <- as.numeric(levels(final$quimen)[final$quimen])
# 
# 
#END REMOVE


# # activite des fip
# table(final[final$quelfic=="FIP","activite"],useNA="ifany")
# summary(final[final$quelfic=="FIP",c("activite","choi","sali","alr","rsti","age")] )
# # activite      # actif occup? 0, ch?meur 1, ?tudiant/?l?ve 2, retrait? 3, autre inactif 4
# 
# final_fip <- final[final$quelfic=="FIP",]
# final_fip <- within(final_fip,{
#   choi <- ifelse(is.na(choi),0,choi)
#   sali <- ifelse(is.na(sali),0,sali)
#   alr <- ifelse(is.na(alr),0,alr)
#   rsti <- ifelse(is.na(rsti),0,rsti)
#   activite <- 2 # TODO comment choisr la valeur par d?faut ?
#   activite <- ifelse(choi > 0,1,activite)
#   activite <- ifelse(sali > 0,0,activite)
#   activite <- ifelse(age  >= 21, 2,activite) # ne peuvent être rattach?s que les ?tudiants  
# })
# final[final$quelfic=="FIP",]<- final_fip
# table(final_fip[,c("age","activite")])
# rm(final_fip)
# 
# print_id(final)
# saveTmp(final, file= "final.Rdata")
#

    final_fip = final.loc[final.quelfic=="FIP", ["choi", "sali", "alr", "rsti","age"]]
    print final_fip.describe()
    
    print set(["choi", "sali", "alr", "rsti"]).difference(set(final_fip.columns))
    for var in  ["choi", "sali", "alr", "rsti"]:
        final_fip[var].fillna(0, inplace=True)
        
    final_fip["activite"] = 2 # TODO comment choisr la valeur par défaut ?
    final_fip.activite = where(final_fip.choi > 0, 1, final_fip.activite)
    final_fip.activite = where(final_fip.sali > 0, 0, final_fip.activite)
    final_fip.activite = where(final_fip.age > 21, 2, final_fip.activite)  # ne peuvent être rattach?s que les ?tudiants  

    final.update(final_fip)
    
    save_temp(final, name="final", year=year)
    
    menagem = load_temp(name="menagem", year=year)
    menagem.rename(columns=dict(ident="idmen",loym="loyer"), inplace=True)
    # TODO : menagem$cstotpragr <- floor(menagem$cstotpr/10)
    
 
    #2008 tau99 removed TODO: check ! and check incidence
    if year == 2008:
        vars = ["loyer", "tu99", "pol99", "reg","idmen", "so", "wprm", "typmen15",
                 "nbinde","ddipl","cstotpragr","champm","zthabm"]
    else:
        vars = ["loyer", "tu99", "pol99", "tau99", "reg","idmen", "so", "wprm", 
                "typmen15", "nbinde","ddipl","cstotpragr","champm","zthabm"]
    famille_vars = ["m_afeamam", "m_agedm","m_clcam", "m_colcam", 'm_mgamm', 'm_mgdomm']

# TODO
# if ("naf16pr" %in% names(menagem)) {
#   naf16pr <- factor(menagem$naf16pr)
#   levels(naf16pr) <-  0:16
#   menagem$naf16pr <- as.character(naf16pr)
#   menagem[is.na(menagem$naf16pr), "naf16pr" ] <- "-1"  # Sans objet 
#   vars <- c(vars,"naf16pr")
# } else if ("nafg17npr" %in% names(menagem)) {
#   # TODO: pb in 2008 with xx
#   if (year == "2008"){
#     menagem[ menagem$nafg17npr == "xx" & !is.na(menagem$nafg17npr), "nafg17npr"] <- "00"
#   }
#   nafg17npr <- factor(menagem$nafg17npr)  
#   levels(nafg17npr) <-  0:17
#   menagem$nafg17npr <- as.character(nafg17npr)
#   menagem[is.na(menagem$nafg17npr), "nafg17npr" ] <- "-1"  # Sans objet
# }
# 


#TODO: TODO: pytohn translation needed
#    if "naf16pr" in menagem.columns:
#        naf16pr <- factor(menagem$naf16pr)
#   levels(naf16pr) <-  0:16
#   menagem$naf16pr <- as.character(naf16pr)
#   menagem[is.na(menagem$naf16pr), "naf16pr" ] <- "-1"  # Sans objet 
#   vars <- c(vars,"naf16pr")
# } else if ("nafg17npr" %in% names(menagem)) {
#   # TODO: pb in 2008 with xx
#   if (year == "2008"){
#     menagem[ menagem$nafg17npr == "xx" & !is.na(menagem$nafg17npr), "nafg17npr"] <- "00"
#   }
#   nafg17npr <- factor(menagem$nafg17npr)  
#   levels(nafg17npr) <-  0:17
#   menagem$nafg17npr <- as.character(nafg17npr)
#   menagem[is.na(menagem$nafg17npr), "nafg17npr" ] <- "-1"  # Sans objet
# }



# # TODO: 2008tau99 is not present should be provided by 02_loy.... is it really needed
    all_vars = list(set(vars).union(set(famille_vars)))
    
    print all_vars
    print  set(menagem.columns)
    available_vars = list( set(all_vars).intersection(set(menagem.columns)))
    
    loyersMenages = menagem.xs(available_vars,axis=1)


# 
# # Recodage de typmen15: modalités de 1:15
# table(loyersMenages$typmen15, useNA="ifany")
# loyersMenages <- within(loyersMenages, {
#   typmen15[typmen15==10 ] <- 1
#   typmen15[typmen15==11 ] <- 2
#   typmen15[typmen15==21 ] <- 3
#   typmen15[typmen15==22 ] <- 4
#   typmen15[typmen15==23 ] <- 5
#   typmen15[typmen15==31 ] <- 6
#   typmen15[typmen15==32 ] <- 7
#   typmen15[typmen15==33 ] <- 8
#   typmen15[typmen15==41 ] <- 9
#   typmen15[typmen15==42 ] <- 10
#   typmen15[typmen15==43 ] <- 11
#   typmen15[typmen15==44 ] <- 12
#   typmen15[typmen15==51 ] <- 13
#   typmen15[typmen15==52 ] <- 14
#   typmen15[typmen15==53 ] <- 15
# })
# 
# 
# TODO: MBJ UNNECESSARY ?
    
    #   On met les non renseignés ie, NA et "" à sans diplome (modalité 7)
    loyersMenages.ddipl = where(loyersMenages.ddipl.isnull(), 7, loyersMenages.ddipl)
    loyersMenages.ddipl = where(loyersMenages.ddipl>1, 
                                loyersMenages.ddipl-1,
                                loyersMenages.ddipl)
    loyersMenages.ddipl.astype("int32")

    final.act5 = NaN    

    final.act5 = where(final.actrec==1, 2, final.act5) # indépendants
    final.act5 = where(final.actrec.isin([2,3]), 1, final.act5)  # salariés

    final.act5 = where(final.actrec==4, 3, final.act5) # chômeur
    final.act5 = where(final.actrec==7, 4, final.act5) # retraité
    final.act5 = where(final.actrec==8, 5, final.act5) # autres inactifs


    # final$wprm <- NULL # with the intention to extract wprm from menage to deal with FIPs
    # final2 <- merge(final, loyersMenages, by="idmen", all.x=TRUE)
    import gc
    del final["wprm"]
    gc.collect()
    final.rename(columns=dict(zthabm="tax_hab"), inplace=True) # rename zthabm to tax_hab
    final2 = final.merge(loyersMenages, on="idmen", how="left") # TODO: Check
    gc.collect()
    # TODO: merging with patrimoine

    apl_imp = read_csv("../../zone_apl/zone_apl_imputation_data.csv")

    print apl_imp.head(10)
    if year == 2008:
        zone_apl = final2.xs(["tu99", "pol99", "reg"], axis=1)
    else:
        zone_apl = final2.xs(["tu99", "pol99", "tau99", "reg"], axis=1)
        
    for i in range(len(apl_imp["TU99"])):
        tu = apl_imp["TU99"][i]
        pol = apl_imp["POL99"][i]
        tau = apl_imp["TAU99"][i]
        reg = apl_imp["REG"][i]

    if year == 2008:
        indices = and_(and_(final2["tu99"] == tu, final2["pol99"] == pol),
                       final2["reg"] == reg)
        selection = and_(and_(apl_imp["TU99"] == tu, apl_imp["POL99"] == pol),
                         apl_imp["REG"] == reg)
    else:
        indices = and_(and_(final2["tu99"] == tu, final2["pol99"] == pol),
                       and_(final2["tau99"] == tau, final2["reg"] == reg))
        selection = and_(and_(apl_imp["TU99"] == tu, apl_imp["POL99"] == pol),
                         and_(apl_imp["TAU99"] == tau, apl_imp["REG"] == reg))
    
    z = random.uniform(size=indices.sum())
    print len(z)
    print len(indices)

    print len(indices)/len(z)
    probs = apl_imp.loc[selection , ["proba_zone1", "proba_zone2"]]
    print probs
    print probs['proba_zone1'].values

    proba_zone_1 =  probs['proba_zone1'].values[0]
    proba_zone_2 =  probs['proba_zone2'].values[0]
    
    final2["zone_apl"] = 3
    final2["zone_apl"][indices] = ( 1 + (z>proba_zone_1) +
                                       (z>(proba_zone_1 + proba_zone_2))) 
    del indices, probs
    
#     control(final2, verbose=True, debug=True, verbose_length=15)
    
    print final2[final2['sali'].isnull()].head(15).to_string()
    print len(final2[final2['sali'].isnull()])
#     columns_w_nan = []
#     for col in final2.columns:
#         if final2[final2['idfoy'].notnull()][col].isnull().any() and not final2[col].isnull().all():
#             columns_w_nan.append(col)
#     print columns_w_nan
#    return
# TODO ?
# # var <- names(foyer)
# #a1 <- c('f7rb', 'f7ra', 'f7gx', 'f2aa', 'f7gt', 'f2an', 'f2am', 'f7gw', 'f7gs', 'f8td', 'f7nz', 'f1br', 'f7jy', 'f7cu', 'f7xi', 'f7xo', 'f7xn', 'f7xw', 'f7xy', 'f6hj', 'f7qt', 'f7ql', 'f7qm', 'f7qd', 'f7qb', 'f7qc', 'f1ar', 'f7my', 'f3vv', 'f3vu', 'f3vt', 'f7gu', 'f3vd', 'f2al', 'f2bh', 'f7fm', 'f8uy', 'f7td', 'f7gv', 'f7is', 'f7iy', 'f7il', 'f7im', 'f7ij', 'f7ik', 'f1er', 'f7wl', 'f7wk', 'f7we', 'f6eh', 'f7la', 'f7uh', 'f7ly', 'f8wy', 'f8wx', 'f8wv', 'f7sb', 'f7sc', 'f7sd', 'f7se', 'f7sf', 'f7sh', 'f7si',  'f1dr', 'f7hs', 'f7hr', 'f7hy', 'f7hk', 'f7hj', 'f7hm', 'f7hl', 'f7ho', 'f7hn', 'f4gc', 'f4gb', 'f4ga', 'f4gg', 'f4gf', 'f4ge', 'f7vz', 'f7vy', 'f7vx', 'f7vw', 'f7xe', 'f6aa', 'f1cr', 'f7ka', 'f7ky', 'f7db', 'f7dq', 'f2da')
# #a2 <- setdiff(a1,names(foyer))
# #b1 <- c('pondfin', 'alt', 'hsup', 'ass_mat', 'zone_apl', 'inactif', 'ass', 'aer', 'code_postal', 'activite', 'type_sal', 'jour_xyz', 'boursier', 'etr', 'partiel1', 'partiel2', 'empl_dir', 'gar_dom', 'categ_inv', 'opt_colca', 'csg_taux_plein','coloc') 
# # hsup feuille d'impot
# # boursier pas dispo
# # inactif etc : extraire cela des donn?es clca etc
# 
# # tester activit? car 0 vaut actif
# table(is.na(final2$activite),useNA="ifany")
# 
# saveTmp(final2, file= "final2.Rdata")

    print_id(final2)

    from src.countries.france.data.erf.build_survey.utilitaries import check_structure
    check_structure(final2)



    from src.countries.france import DATA_SOURCES_DIR
    test_filename = os.path.join(DATA_SOURCES_DIR,"test.h5") 
    store = HDFStore(test_filename)
    store['survey_'+ str(year)]  = final2
    
if __name__ == '__main__':

    final()
