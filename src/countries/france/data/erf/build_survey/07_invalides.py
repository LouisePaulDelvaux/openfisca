# -*- coding:utf-8 -*-
# Created on 21 mai 2013
# This file is part of OpenFisca.
# OpenFisca is a socio-fiscal microsimulation software
# Copyright ©2013 Clément Schaff, Mahdi Ben Jelloul
# Licensed under the terms of the GVPLv3 or later license
# (see openfisca/__init__.py for details)
# # # OpenFisca

from numpy import where, array, NaN
from src.countries.france.data.erf.datatable import DataCollection
from src.countries.france.data.erf.build_survey import show_temp, load_temp, save_temp
from src.countries.france.data.erf.build_survey.utilitaries import control
from numpy import logical_not as not_
from numpy import logical_and as and_
from numpy import logical_or as or_
from pandas import concat, DataFrame
from src.countries.france.data.erf.build_survey.utilitaries import print_id



# # 
# # ##***********************************************************************/
# # message('07_invalides: construction de la variable invalide')
# # ##***********************************************************************/
def invalide(year = 2006):
    
    print 'Entering 07_invalides: construction de la variable invalide'
    

# # # Invalides
# # #inv = caseP (vous), caseF (conj) ou case G, caseI, ou caseR (pac)
# # 
# # loadTmp("final.Rdata")
# # invalides <- final[,c("noindiv","idmen","caseP","caseF","idfoy","quifoy")]
# # invalides <- within(invalides,{
# #   caseP <- ifelse(is.na(caseP),0,caseP)
# #   caseF <- ifelse(is.na(caseF),0,caseF)
# #   inv <- FALSE})
# # # Les "vous" invalides
# # table(invalides[,c("caseF","quifoy")],useNA="ifany")
# # invalides[(invalides$caseP==1) & (invalides$quifoy=="vous"),"inv"] <- TRUE
# # 
    print 'Etape 1 création de la df invalides'
    final = load_temp(name="final", year=year)
    invalides = final.xs(["noindiv","idmen","caseP","caseF","idfoy","quifoy"], axis=1)
    
    
    for var in ["caseP", "caseF"]:  
        assert invalides[var].notnull().all(), 'présence de NaN dans %s' %(var)
     

    # Les déclarants invalides
    invalides['inv'] = False
    invalides['inv'][(invalides['caseP']==1) & (invalides['quifoy']==0)] = True
    
    assert invalides["inv"].notnull().all()
    print_id(invalides)


    print invalides["inv"].sum(), " invalides déclarants"

# # # Les conjoints invalides
# # 
# # #men_inv_conj <- invalides[c("idmen","caseF","quifoy")] 
# # #men_inv_conj <- rename(men_inv_conj, c("caseF"="inv"))
# # #table(men_inv_conj[men_inv_conj$inv==1 ,c("inv","quifoy")],useNA="ifany")
# # # Il y a des caseF suir des conjoints cela vint des doubles d?clarations TODO shoumd clean this
# # #toto <- invalides[invalides$caseF==1 & invalides$quifoy=="conj","idmen"]
# # #load(indm)
# # #titi <- indivim[(indivim$ident %in% toto) & (indivim$persfip=="vous" |indivim$persfip=="conj") ,c("ident","noindiv","declar1","declar2","persfip","quelfic")]
# # #titi <- titi[order(titi$ident),]
# # foy_inv_conj <- invalides[,c("idfoy","caseF","quifoy")] 
# # foy_inv_conj <- rename(foy_inv_conj, c("caseF"="inv"))
# # table(foy_inv_conj[ ,c("inv","quifoy")],useNA="ifany")
# # # On ne garde donc que les caseF des "vous"

# # foy_inv_conj   <- foy_inv_conj[foy_inv_conj$quifoy=="vous",c("idfoy","inv")]
# # table(foy_inv_conj[ ,c("inv")],useNA="ifany")
# # invalides_conj <- invalides[invalides$quifoy=="conj",c("idfoy","noindiv")]
# # invalides_conj <- merge(invalides_conj, foy_inv_conj, by="idfoy", all.x=TRUE)
# # table(invalides_conj$inv) # TODO en 2006 On en a 316 au lieu de 328 il doit y avoir de idfoy avec caseF qui n'ont pas de vous because double déclaration'   
# # invalides[invalides$quifoy=="conj",c("idfoy","noindiv","inv")] <- invalides_conj
# # table(invalides[,c("inv","quifoy")],useNA="ifany")
# # rm(invalides_conj,foy_inv_conj)

    # On récupère les idfoy des foyers avec une caseF cochée 

    idfoy_inv_conj = final["idfoy"][final["caseF"]]
    print idfoy_inv_conj.head()
    inv_conj_condition = and_(invalides["idfoy"].isin(idfoy_inv_conj), (invalides["quifoy"]==1))    
    invalides["inv"][inv_conj_condition] = True

    print invalides["inv"].sum(), " invalides à la fois déclarants et conjoints"
    
# # # Enfants invalides et garde alternée
# # 
# # loadTmp("pacIndiv.Rdata")
# # foy_inv_pac <- invalides[!(invalides$quifoy %in% c("vous","conj")),c("inv","noindiv")] 
# # foy_inv_pac <- merge(foy_inv_pac, pacIndiv[,c("noindiv","typ","naia")], by="noindiv",all.x =TRUE)
# # names(foy_inv_pac)
# # table(foy_inv_pac[,c("typ","naia")],useNA="ifany")
# # table(foy_inv_pac[,c("typ")],useNA="ifany")
# # foy_inv_pac <- within(foy_inv_pac,{
# #   inv  <- (typ=="G") | (typ=="R") | (typ=="I") | (typ=="F" & (as.numeric(year)-naia>18))
# #   alt  <- (typ=="H") | (typ=="I")
# #   naia <- NULL
# #   typ  <- NULL})
# # 
# # table(foy_inv_pac[ ,c("inv")],useNA="ifany")
# # table(foy_inv_pac[ ,c("alt")],useNA="ifany")
# # invalides$alt <- 0
# # foy_inv_pac[is.na(foy_inv_pac$alt),"alt"] <- 0
# # invalides[!(invalides$quifoy %in% c("vous","conj")),c("noindiv","inv","alt")] <- foy_inv_pac
# # table(invalides$inv==1,useNA="ifany")
# # table(invalides$alt==1,useNA="ifany")
# # rm(foy_inv_pac,pacIndiv)
# # 

    # enfants invalides et garde alternée
    
    pacIndiv = load_temp(name='pacIndiv', year=year)
    foy_inv_pac = invalides.loc[not_(invalides.quifoy.isin([0, 1])), ['noindiv', 'inv']]
    
    pac = pacIndiv.ix[:, ["noindiv", "type_pac", "naia"]]

    foy_inv_pac = foy_inv_pac.merge(pacIndiv.loc[:, ['noindiv', 'type_pac', 'naia']], 
                                    on='noindiv', how='outer')
    print foy_inv_pac.ix[:,['type_pac', 'naia']].describe()
#     foy_inv_pac['inv'] = ((foy_inv_pac['type_pac']=="G")|(foy_inv_pac['type_pac']=="R")|
#                           (foy_inv_pac['type_pac']=="I") | (foy_inv_pac['type_pac']=="F" & 
#                         (year - foy_inv_pac['naia']>18)))
    foy_inv_pac['inv'] = or_(foy_inv_pac['type_pac']=="G", or_(foy_inv_pac['type_pac']=="R",
                            or_(foy_inv_pac['type_pac']=="I", and_(foy_inv_pac['type_pac']=="F", 
                                (year - foy_inv_pac['naia'])>18))))
    print foy_inv_pac.inv.describe() # TODO: JS : que des false là-dedans
    
    foy_inv_pac['alt'] = ((foy_inv_pac['type_pac']=="H") | (foy_inv_pac['type_pac']=="I"))
    foy_inv_pac['naia'] = None
    foy_inv_pac['type_pac'] = None
    
    print foy_inv_pac['inv'].describe()
    invalides['alt'] = 0
    foy_inv_pac['alt'][foy_inv_pac.alt.isnull()] = 0
    invalides = invalides.merge(foy_inv_pac, on=["noindiv","inv","alt"])
    invalides = invalides.drop_duplicates(['noindiv', 'inv', 'alt'], take_last=True)
    
    print invalides[invalides['inv']==1].describe()
    print invalides[invalides['alt']==1].describe()
    del foy_inv_pac,pacIndiv
    
# # # Initialisation des NA sur alt et inv
# # invalides[is.na(invalides$inv), "inv"] <- 0
# # table(invalides[,c("alt","inv")],useNA="ifany")
# # 
# # final <- merge(final, invalides[,c("noindiv","inv","alt")], by="noindiv",all.x=TRUE)
# # table(final[, c("inv","alt")],useNA="ifany")
    print 'Initialisation des NA sur alt et inv'
    invalides['inv'][invalides.inv.isnull()] = 0
    print invalides['inv'].describe()
    
    final = final.merge(invalides.loc[:, ['noindiv', 'inv', 'alt']], on='noindiv', how='left')
    control(final, debug=True)
    print final.loc[:,['inv', 'alt']].describe()
    print final.inv.value_counts()
    return
# # rm(invalides)
# # saveTmp(final, file= "final.Rdata")
    print 'Sauvegarde :'
    del invalides
    save_temp(final, name='final', year=year)

if __name__ == '__main__':
    invalide()