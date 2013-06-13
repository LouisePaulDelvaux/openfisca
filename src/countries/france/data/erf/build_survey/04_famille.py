# -*- coding:utf-8 -*-
# Created on 21 mai 2013
# This file is part of OpenFisca.
# OpenFisca is a socio-fiscal microsimulation software
# Copyright ©2013 Clément Schaff, Mahdi Ben Jelloul
# Licensed under the terms of the GVPLv3 or later license
# (see openfisca/__init__.py for details)

from numpy import where, array, NaN
from src.countries.france.data.erf.datatable import DataCollection
from src.countries.france.data.erf.build_survey import show_temp, load_temp, save_temp
from numpy import logical_not as not_
from numpy import logical_and as and_
from numpy import logical_or as or_
import pdb
from pandas import concat, DataFrame

# OpenFisca
# Retreives the families 
# Creates 'idfam' and 'quifam' variables

##***********************************************************************/
print('04_famille: construction de la table famille')
##***********************************************************************/

def subset_base(base,famille):
    """
    generates a dataframe containing the values of base that are not already in famille
    """
    print "base", len(base.index)
    tmp = base[not_(base.noindiv.isin(famille.noindiv.values))]
    return tmp


def famille(year=2006):
### On suit la méthode décrite dans le Guide ERF_2002_rétropolée page 135
#
#if (year=="2006") {
#  smic = 1254
#  } else if (year=="2007") {
#    smic = 1280    
#  } else if (year=="2008") {
#     smic = 1308    
#  } else if (year=="2009") {
#    smic = 1337
#  } else {
#    message("smic non défini")
#  }
#
    
    if year == 2006: 
        smic = 1254
    elif year == 2007: 
        smic = 1280    
    elif year == 2008: 
        smic = 1308    
    elif year==2009: 
        smic = 1337
    else: 
        print("smic non défini")
    
    #indVar = c('noi','noicon','noindiv','noiper','noimer','ident','declar1','naia','naim','lien','quelfic','acteu','stc','contra','titc','mrec',
    #            'forter','rstg','retrai','lpr','cohab','ztsai','sexe','persfip','agepr','rga','actrec')
    #
    
    individual_vars = ['noi','noicon','noindiv','noiper','noimer','ident','declar1','naia','naim','lien','quelfic',
                       'acteu','stc','contra','titc','mrec','forter','rstg','retrai','lpr','cohab','ztsai','sexe',
                       'persfip','agepr','rga','actrec']

## TODO check if we can remove acteu forter etc since dealt with in 01_pre_proc 
#
#indivi <- LoadIn(indm,indVar)

    
#    indivi = erf_indivi.merge(eec_indivi)
    indivi = load_temp(name="indivim", year=year)
#
#indivi <- within(indivi,{
#          year <- as.numeric(year)
#          noidec <- as.numeric(substr(declar1,1,2))
#          agepf <- ifelse(naim < 7, year-naia ,year-naia-1)
#          })
    indivi['year'] = year
    indivi["noidec"] =   indivi["declar1"].apply(lambda x: str(x)[0:2])
    indivi["agepf"] = where(indivi['naim'] < 7, indivi['year'] - indivi['naia'] ,
                            indivi['year'] - indivi['naia'] - 1)
#table(indivi$acteu)
#
### On enlève les enfants en nourrice...*/
#indivi2 <- subset(indivi,lien==6 & agepf <  16 & quelfic=='EE','noindiv')
#indivi <- indivi[!indivi$noindiv %in% indivi2$noindiv,]
#rm(indivi2)

    indivi = indivi[ not_((indivi['lien']==6) & (indivi['agepf']<16) & ("quelfic"=="EE"))]

# # ## Enfant à naître (NN pour nouveaux nés)
# # indVar = c('noi','noicon','noindiv','noiper','noimer','ident','declar1','naia','naim','lien','quelfic','acteu','stc','contra','titc','mrec',
# #            'forter','rstg','retrai','lpr','cohab','ztsai','sexe','persfip','agepr','rga','actrec',
# #            "agepf","noidec","year")
    print 'Enfant à naître----------------'
    
    indVar = ['noi','noicon','noindiv','noiper','noimer','ident','declar1','naia','naim','lien','quelfic','acteu','stc','contra','titc','mrec',
            'forter','rstg','retrai','lpr','cohab','ztsai','sexe','persfip','agepr','rga','actrec',
            "agepf","noidec","year"]
    
# # enfnn <- LoadIn(enfnnm,indVar)
    enfnn = load_temp(name='enfnn', year=year)
    enfnn = enfnn.loc[:, indVar] #NOTE: la moitié des colonnes est remplie avec des NaN

# # ## Remove duplicated  noindiv because some rga are different
# # enfnn <- enfnn[!duplicated(enfnn[,"noindiv"]),]
# # ## On enlève les enfants à naitre qui ne sont pas les enfants de la personne de référence
# # enfnn <- subset(enfnn,lpr==3)
# # enfnn <- enfnn[(!enfnn$noindiv %in% indivi$noindiv),]
    enfnn = enfnn.drop_duplicates('noindiv')
    print 'nb enfants à naitre', len(enfnn.index)
    print 'On enlève les enfants à naitre qui ne sont pas les enfants de la personne de référence'
    enfnn = enfnn[enfnn['lpr']==3]
    enfnn = enfnn[not_(enfnn.noindiv.isin(indivi.noindiv.values))]
    print len(enfnn.index)

# # # PB with vars "agepf"  "noidec" "year"  NOTE: quels problèmes ? JS
# # base <- rbind(indivi,enfnn)
# # setdiff(names(indivi),names(enfnn))
# # table(base$quelfic)
# # 
# # dup <- duplicated(base[,c("noindiv")])
# # #dup <- duplicated(base)
# # table(dup)
# # 
# # str(base)
    base = concat([indivi, enfnn])
    print 'length of base', len(base.index)
    
# # # Preparing the dataframe base :
# # base <- within(base,{
# #   noindiv<- 100*ident + noi
# #   m15 <- (agepf<16) 
# #   p16m20 <- ((agepf>=16) & (agepf<=20))
# #   p21 <- (agepf>=21)
# #   ztsai[is.na(ztsai)] <- 0
# #   smic55 <- (ztsai>= smic*12*0.55)   ##55% du smic mensuel brut */
# #   famille <- 0
# #   kid <- FALSE})
    base['noindiv'] = 100*base['ident'] + base['noi']
    base['m15'] = (base['agepf']<16)
    base['p16m20'] = ((base['agepf']>=16) & (base['agepf']<=20))
    base['p21'] = (base['agepf']>=21)
    base['ztsai'] = where(base['ztsai'] is None, 0, base['ztsai'])
    base['smic55'] = (base['ztsai'] >= smic*12*0.55) ##55% du smic mensuel brut
    base['famille'] = 0
    base['kid'] = False
    print base.head()
    
    def control(dataframe):
        print 'longueur de la dataframe après opération =', len(dataframe.index)
        dup = dataframe.duplicated(cols='noindiv')
        print 'contrôle des doublons =>', any(dup==True) #dup.describe()
        print 'contrôle des colonnes ->', len(dataframe.columns)
        print 'nombre de familles différentes', len(set(famille.noifam.values))
        print 'contrôle noifam is null:', len(dataframe[dataframe['noifam'].isnull()])
        if len(dataframe.index) > len(base.index): raise Exception('too many rows compared to base')
    
# # ##******************************************************************************************************************/
# # message('Etape 1: On cherche les enfants ayant père et/ou mère')
# # pr <- subset(base,lpr==1,c('ident','noi'))
# # pr$noifam <- 100*pr$ident + pr$noi
# # pr <- pr[c('ident','noifam')]
# # 
# # nof01 <- subset(base,(lpr %in% c(1,2) )|(lpr==3 & m15) | (lpr==3 & (p16m20 & !smic55) )) 
# # nof01 <- merge(pr,nof01,by ='ident')
# # nof01 <- within(nof01,{
# #   famille <- 10
# #   kid <-(lpr==3 & m15) | (lpr==3 & (p16m20 & !smic55 ) )
# #   })
# # famille <- nof01
# # table(famille$famille,useNA='ifany')
# # rm(nof01)
# # ##******************************************************************************************************************/
    print 'Etape 1 : On cherche les enfants ayant père et/ou mère'
    
    pr = base[base['lpr']==1].loc[:, ['ident', 'noi']]
    pr['noifam'] = 100*pr['ident'] + pr['noi']
    pr = pr.loc[:, ['ident', 'noifam']]
    print 'length pr', len(pr.index)
    
    nof01 = base[(base.lpr.isin([1,2])) | (base['lpr'] == 3 & base['m15']) |
                 (base['lpr'] == 3 & (base['p16m20'] & not_(base['smic55'])) )]
    print 'longueur de nof01 avant merge', len(nof01.index)
    nof01 = nof01.merge(pr, on='ident', how='outer')
    nof01['famille'] = 10
    nof01['kid'] = ((nof01['lpr']==3 & nof01['m15']) | 
                    (nof01['lpr']==3 & (nof01['p16m20'] & not_(nof01['smic55']))))
    famille = nof01
    del nof01
    control(famille)


    
# # message('Etape 2a')
# # ## l'identifiant est le noi de l'homme
# # ## cohab=1  vit en couple
# # ## cohab=2 ou cohab=0 ne vit pas en couple
# # hcouple <- base[(!base$noindiv %in% famille$noindiv),] 
# # hcouple <- subset(hcouple,(cohab==1) & (lpr>=3) & (sexe==1))
# # hcouple <- within(hcouple,{
# #   noifam=100*ident + noi ## l'identifiant est la personne de référence du ménage  */
# #     famille = 21 })
    print 'Etape 2a : identification des couples------------------------'
    # l'ID est le noi de l'homme
    hcouple = subset_base(base,famille)
    hcouple = hcouple[(hcouple['cohab']==1) & (hcouple['lpr']>=3) & (hcouple['sexe']==1)]
    hcouple['noifam'] = 100*hcouple['ident'] + hcouple['noi']
    hcouple['famille'] = 21
    print 'longueur hcouple', len(hcouple.index)

# # message('Etape 2b')
# # fcouple<- base[!base$noindiv %in% famille$noindiv,]
# # fcouple <- subset(fcouple,(cohab==1) & (lpr>=3) & (sexe==2))
# # fcouple <- within(fcouple,{
# #     noifam <- 100*ident + noicon ## l'identifiant est le conjoint du ménage  */
# #     famille <- 22 })
# # 
# # famcom<- merge(fcouple['noifam'],hcouple['noifam'])
# # fcouple <- merge(famcom,fcouple)
# # 
# # famille <- rbind(famille,hcouple,fcouple)
# # dup <- duplicated(famille$noindiv)
# # table(dup)
# # table(famille$famille,useNA='ifany')
# # rm(hcouple,fcouple,famcom)
    print 'Etape 2b : attributing the noifam to the wives-------------------'
    fcouple = base[not_(base.noindiv.isin(famille.noindiv.values))]
    fcouple = fcouple[(fcouple['cohab']==1) & (fcouple['lpr']>=3) & (fcouple['sexe']==2)]
    fcouple['noifam'] = 100*fcouple['ident'] + fcouple['noi']
    fcouple['famille'] = 22
    print 'longueur fcouple', len(fcouple.index)
    
    famcom = fcouple.merge(hcouple, on='noifam', how='outer')
    print 'longueur fancom après fusion', len(famcom.index)
    fcouple = fcouple.merge(famcom) #NOTE : faire un inner merge sinon présence de doublons
    print 'longueur fcouple après fusion', len(fcouple.index)

    famille = concat([famille, hcouple, fcouple], join='inner')
    control(famille)

# # ##******************************************************************************************************************/
# # message('Etape 3: personnes seules')
# # message(' 3.1 personnes seules 1')
# # seul1 <- base[(!base$noindiv %in% famille$noindiv),] 
# # seul1 <- subset(seul1,(lpr %in% c(3,4)) & ( (p16m20 & smic55)|p21 ) & (cohab==1) & (sexe==2))
# # if (nrow(seul1) > 0){
# #   seul1 <- within(seul1,{noifam <- 100*ident+noi
# #                        famille <- 31})
# #   famille <- rbind(famille,seul1)
# #   dup <- duplicated(famille$noindiv)
# #   table(dup)
# # }
    print 'Etape 3: personnes seules---------------------'
    print '    3.1 : personnes seules de catégorie 1'
    seul1 = base[not_(base.noindiv.isin(famille.noindiv.values))]
    seul1 = seul1[(seul1.lpr.isin([3,4])) & ((seul1['p16m20'] & seul1['smic55'])|seul1['p21']) & (seul1['cohab']==1) &
                  (seul1['sexe']==2)]
    if len(seul1.index)>0:
        seul1['noifam'] = 100*seul1['ident'] + seul1['noi']
        seul1['famille'] = 31
        famille = concat([famille, seul1])
    print len(seul1.index)
    control(famille)
    
# # message('  3.2 personnes seules 2')
# # seul2 <- base[(!base$noindiv %in% famille$noindiv),] 
# # seul2 <- subset(seul2,(lpr %in% c(3,4)) & p16m20 & smic55 & (cohab!=1))
# # seul2 <- within(seul2,{noifam <- 100*ident+noi
# #                      famille <- 32})
# # famille <- rbind(famille,seul2)
    print '    3.1 personnes seules type 2'
    seul2 = base[not_(base.noindiv.isin(famille.noindiv.values))]
    seul2 = seul2[(seul2.lpr.isin([3,4])) & seul2['p16m20'] & seul2['smic55'] & (seul2['cohab'] != 1)]
    seul2['noifam'] = 100*seul2['ident'] + seul2['noi']
    seul2['famille'] = 32
    famille = concat([famille, seul2])
    control(famille)
    
# # message(' 3.3 personnes seules 3')
# # seul3 <- base[(!base$noindiv %in% famille$noindiv),] 
# # seul3 <- subset(seul3,(lpr %in% c(3,4)) & p21 & cohab!=1)
# #     ## TODO CHECK erreur dans le guide méthodologique ERF 2002 lpr 3,4 au lieu de 3 seulement */
# # seul3 <- within(seul3,{noifam=100*ident+noi
# #                          famille = 33})
# # famille <- rbind(famille,seul3)
# # dup <- duplicated(famille$noindiv)
# # table(dup)
    print '    3.3 personnes seules de type 3'
    seul3 = subset_base(base,famille)
    seul3 = seul3[(seul3.lpr.isin([3,4])) & seul3['p21'] & (seul3['cohab'] != 1)]
    seul3['noifam'] = 100*seul3['ident'] + seul3['noi']
    seul3['famille'] = 33
    famille = concat([famille, seul3])
    control(famille)
    
# # message(' 3.4 personnes seules 4')
# # seul4 <- base[(!base$noindiv %in% famille$noindiv),] 
# # seul4 <- subset(seul4,(lpr==4) & p16m20 & !smic55 & noimer==0 & noiper==0 & persfip=="vous")
# # 
# # if (nrow(seul4) >0 ) {  # 2006, 2009 pas de personne seule (sans enfant fip)
# #   seul4 <- within(seul4,{noifam = 100*ident + noi
# #                          famille = 34})
# # }
# # 
# # famille <- rbind(famille,seul4)
# # dup <- duplicated(famille$noindiv)
# # table(dup)
# # 
# # table(famille$famille,useNA='ifany')
# # rm(seul1,seul2,seul3,seul4)
    print '    3.4 : personnes seules de type 4'
    seul4 = subset_base(base,famille)
    seul4 = seul4[(seul4['lpr']==4) & seul4['p16m20'] & not_(seul4['smic55']) & (seul4['noimer']==0) &
                  (seul4['persfip']=='vous')]
    
    if len(seul4.index)>0:
        seul4['noifam'] = 100*seul4['ident'] + seul4['noi']
        seul4['famille'] = 34
        famille = concat([famille, seul4])
    control(famille)
    
# # ##******************************************************************************************************************/
# # message('Etape 4')  
# # message(' 4.1 enfant avec mère')
# # avec_mere <- base[(!base$noindiv %in% famille$noindiv),] 
# # avec_mere <- subset(avec_mere,((lpr=4) & ( (p16m20=1) | (m15=1))) & noimer!=0)
# # 
# # avec_mere <- within(avec_mere,{noifam=100*ident + noimer
# #              famille=41
# #              kid=TRUE})
# # 
# # ## on récupère les mères */
# # mereid <- upData(avec_mere['noifam'], rename = c(noifam = 'noindiv'));
# # mereid <- unique(mereid)
# # 
# # mere <- merge(mereid,base)
# # mere <- within(mere,{noifam=100*ident + noi
# #                      famille=42})
# # # TODO il y a deux mères qui ne sont pas dans les individus (problème des conjoints fip ? MBJ ne comprends pas) : 
# # dim(mereid)
# # dim(mere)
# # # TODO on préfère  donc enlever leurs enfants
# # avec_mere <- avec_mere[avec_mere$noifam %in% mere$noifam,]
# # 
    print 'Etape 4 : traitement des enfants'
    print '    4.1 : enfant avec mère'
    avec_mere = subset_base(base,famille)
    avec_mere =  avec_mere[((avec_mere['lpr']==4) & ((avec_mere['p16m20']==1) | (avec_mere['m15']==1)) &
                           (avec_mere['noimer'] != 0))]
    avec_mere['noifam'] = 100*avec_mere['ident'] + avec_mere['noimer']
    avec_mere['famille'] = 41
    avec_mere['kid'] = True
    
    #On récupère les mères des enfants
    mereid = DataFrame(avec_mere['noifam'])
    mereid.columns = ['noindiv']
    mereid = mereid.drop_duplicates()
    
    mere = mereid.merge(base)   
    mere['noifam'] = 100*mere['ident'] + mere['noi']
    mere['famille'] = 42 #H2G2 nous voilà
    avec_mere = avec_mere[avec_mere.noifam.isin(mere.noifam.values)]
    print 'contrôle df mère'
    control(mere)
    
# # conj_mere <- merge(conj_mereid,base)
# # conj_mere$famille <- 43
# # 
# # famille <- famille[(!famille$noindiv %in% mere$noindiv),] 
# # 
# # ## on récupère les conjoints des mères */
# # conj_mereid <- mere[mere$noicon!=0,c('ident','noicon','noifam')]
# # 
# # conj_mereid$noindiv = 100*conj_mereid$ident + conj_mereid$noicon
# # conj_mereid <- conj_mereid[c('noindiv','noifam')]
# # 
# # conj_mere <- merge(conj_mereid,base)
# # conj_mere$famille <- 43
# # 
# # famille <- famille[(!famille$noindiv %in% conj_mere$noindiv),] 
# # famille <- rbind(famille,avec_mere,mere,conj_mere)
# # 
# # dup <- duplicated(famille$noindiv)
# # table(dup)
# # table(famille$famille,useNA='ifany')
# # rm(avec_mere,mere,mereid,conj_mere,conj_mereid)

    famille = famille[not_(famille.noindiv.isin(mere.noindiv.values))]
    control(famille)
    
    #on retrouve les conjoints des mères
    conj_mereid = mere[mere['noicon']!=0].loc[:, ['ident', 'noicon', 'noifam']]
    conj_mereid['noindiv'] = 100*conj_mereid['ident'] + conj_mereid['noicon']
    conj_mereid = conj_mereid.loc[:, ['noindiv', 'noifam']]
    conj_mereid = conj_mereid.merge(base)
    control(conj_mereid)
    
    conj_mere = conj_mereid.merge(base)
    conj_mere['famille'] = 43
    
    famille = famille[not_(famille.noindiv.isin(conj_mere.noindiv.values))]
    famille = concat([famille, avec_mere, mere, conj_mere])
    control(famille)
    del avec_mere, mere, conj_mere, mereid, conj_mereid

# # message(' 4.2 enfants avec père')
# # avec_pere <- base[(!base$noindiv %in% famille$noindiv),] 
# # avec_pere <- subset(avec_pere,((lpr=4) & ( (p16m20=1) | (m15=1))) & noiper!=0)
# # avec_pere <- within(avec_pere,{noifam=100*ident + noiper
# #              famille=44
# #              kid=TRUE})
# # 
# # ## on récupère les pères  pour leur attribuer une famille propre */
# # pereid <- upData(avec_pere['noifam'], rename = c(noifam = 'noindiv'));
# # pereid <- unique(pereid)
# # pere <- merge(pereid,base)
# # pere <- within(pere,{noifam=100*ident + noi
# #                        famille=45})
# # 
# # famille <- famille[(!famille$noindiv %in% pere$noindiv),] 
# # 
# # ## on récupère les conjoints des pères */
# # conj_pereid <- pere[pere$noicon!=0,c('ident','noicon','noifam')]
# # conj_pereid$noindiv = 100*conj_pereid$ident + conj_pereid$noicon
# # conj_pereid <- conj_pereid[c('noindiv','noifam')]
# # 
# # conj_pere <- merge(conj_pereid,base)
# # if (nrow(conj_pere) >0) conj_pere$famille <- 46
# # # 2006: erreur pas de conjoint de père ?
# # 
# # famille <- famille[(!famille$noindiv %in% conj_pere$noindiv),] 
# # famille <- rbind(famille,avec_pere,pere,conj_pere)
# # dup <- duplicated(famille$noindiv)
# # table(dup)
    print '    4.2 : enfants avec père'
    avec_pere = subset_base(base,famille)
#     avec_pere = avec_pere[and_(avec_pere['lpr']==4,
#                           and_(or_((avec_pere['p16m20']==1), (avec_pere['m15']==1)), 
#                           avec_pere['noiper'].notnull()))]
    avec_pere = avec_pere[(avec_pere['lpr']==4) &
                          or_((avec_pere['p16m20']==1), (avec_pere['m15']==1)) & 
                          (avec_pere['noiper'].notnull())]
    avec_pere['noifam'] = 100*avec_pere['ident'] + avec_pere['noiper']
    avec_pere['famille'] = 44
    avec_pere['kid'] = True
    print 'check of presence of NaN in avec_pere',len(avec_pere[avec_pere['noifam'].isnull()].index)


    pereid = DataFrame(avec_pere['noifam']); pereid.columns = ['noindiv']
    pereid = pereid.drop_duplicates()
    pere = base.merge(pereid, on='noindiv', how='inner')
    
    pere['noifam'] = 100*pere['ident'] + pere['noi']
    pere['famille'] = 45
    famille = famille[not_(famille.noindiv.isin(pere.noindiv.values))]
    
    #On récupère les conjoints des pères
    conj_pereid = pere.loc[array(pere['noicon']!=0), ['ident','noicon','noifam']]
    conj_pereid['noindiv'] = 100*conj_pereid['ident'] + conj_pereid['noicon']
    conj_pereid = conj_pereid.loc[:, ['noindiv','noifam']]
    
    conj_pere = base.merge(conj_pereid, on=['noindiv'] ,how='inner')
    control(conj_pere)
    if len(conj_pere.index)>0 : conj_pere['famille'] = 46
        
    famille = famille[not_(famille.noindiv.isin(conj_pere.noindiv.values))]
    famille = concat([famille, avec_pere, pere, conj_pere])
    control(famille)
    
# # 
# # table(famille$famille,useNA='ifany')
# # rm(avec_pere,pere,pereid,conj_pere,conj_pereid)
    del avec_pere,pere,pereid,conj_pere,conj_pereid
    
# # ##* 42. enfants avec déclarant */
# # avec_dec <- base[(!base$noindiv %in% famille$noindiv),] 
# # avec_dec <- subset(avec_dec,(persfip=="pac") & (lpr=4) &  ( (p16m20&!smic55) | (m15=1 )))
# # avec_dec <- within(avec_dec,{noifam = 100*ident + noidec
# #             famille=47
# #             kid=TRUE})
# # 
# # ## on récupère les déclarants pour leur attribuer une famille propre */
# # decid <- upData(avec_dec['noifam'], rename = c(noifam = 'noindiv'));
# # decid <- unique(decid)
# # 
# # dec <- merge(decid,base)
# # dec <- within(dec,{noifam=100*ident + noi
# #                    famille=48})
# # 
# # famille <- famille[(!famille$noindiv %in% dec$noindiv),] 
# # famille <- rbind(famille,avec_dec,dec)
# # dup <- duplicated(famille$noindiv)
# # table(dup)
# # 
# # table(famille$famille,useNA='ifany')
# # rm(dec,decid,avec_dec)
    print '    4.3 : enfants avec déclarant'
    avec_dec = subset_base(base,famille)
    avec_dec = avec_dec[(avec_dec['persfip']=="pac") & (avec_dec['lpr']==4) &
                    ( (avec_dec['p16m20'] & not_(avec_dec['smic55'])) | (avec_dec['m15']==1 ))]
    avec_dec['noifam'] = 100*avec_dec['ident'] + avec_dec['noidec'].astype('float')
    avec_dec['famille'] = 47
    avec_dec['kid'] = True
    control(avec_dec)
    
    #on récupère les déclarants pour leur attribuer une famille propre
    decid = DataFrame(avec_dec['noifam']) ; decid.columns = ['noindiv']
    decid = decid.drop_duplicates()
    dec = base.merge(decid, how='inner')
    dec['noifam'] = 100*dec['ident'] + dec['noi']
    dec['famille'] = 48
    
    famille = famille[not_(famille.noindiv.isin(dec.noindiv.values))]
    famille = concat([famille, avec_dec, dec])
    del dec, decid, avec_dec
    control(famille)
    
# # 
# # ##******************************************************************************************************************/
# # ## famille etape 5 : enfants fip */ 
# # message('Etape 5 : enfants fip')
# # # On rajoute les enfants fip 
# # # (on le fait ici pour que cela n'interfère pas avec les recherches précédentes)
# # fip <- LoadIn(fipDat)
# # 
# # indVar = c('noi','noicon','noindiv','noiper','noimer','ident','declar1','naia','naim','lien','quelfic','acteu','stc','contra','titc','mrec',
# #             'forter','rstg','retrai','lpr','cohab','ztsai','sexe','persfip','agepr','rga')
# # 
# # fip <- fip[c(indVar,'actrec','agepf','noidec','year')]
# # 
# # table(duplicated(fip$noindiv))
# # 
# # ## Variables auxilaires présentes dans base qu'il faut rajouter aux fip'
# # ## WARNING les noindiv des fip sont construits sur les ident des déclarants
# # ## pas d'orvelap possible avec les autres noindiv car on a des noi =99, 98, 97 ,...'
# # names(fip)
# # 
# # fip <- within(fip,{
# #   m15 <- (agepf<16) 
# #   p16m20 <- ((agepf>=16) & (agepf<=20))
# #   p21 <- (agepf>=21)
# #   ztsai[is.na(ztsai)] <- 0
# #   smic55 <- (ztsai >= smic*12*0.55)   ## 55% du smic mensuel brut */
# #   famille <- 0
# #   kid <- FALSE
# # })
# # 
# # dup<-duplicated(fip$noindiv)
# # table(dup)
# # 
    print 'Etape 5 : récupération des enfants fip-----------'
    print '    5.1 : création de la df fip'
    fip = load_temp(name='fipDat', year=year)
    indVar_fip = ['noi','noicon','noindiv','noiper','noimer','ident','declar1','naia','naim','lien','quelfic','acteu','stc','contra','titc','mrec',
            'forter','rstg','retrai','lpr','cohab','ztsai','sexe','persfip','agepr','rga','actrec','agepf','noidec','year']
    fip = fip.loc[:, indVar_fip]

    # Variables auxilaires présentes dans base qu'il faut rajouter aux fip'
    # WARNING les noindiv des fip sont construits sur les ident des déclarants
    # pas d'orvelap possible avec les autres noindiv car on a des noi =99, 98, 97 ,...'
    fip['m15'] = (fip['agepf']<16)
    fip['p16m20'] = ((fip['agepf']>=16) & (fip['agepf']<=20))
    fip['p21'] = (fip['agepf']>=21)
#     fip['ztsai'][fip['ztsai'] is None] = 0 #there are alrdy zeros
    fip['smic55'] = (fip['ztsai'] >= smic*12*0.55)
    fip['famille'] = 0
    fip['kid'] = False
    print fip['ztsai'].isnull().describe()

# # base <- rbind(base,fip)
# # table(base$quelfic)

# # enfant_fip <- base[(!base$noindiv %in% famille$noindiv),] 
# # enfant_fip <- subset(enfant_fip, (quelfic=="FIP") & (( (agepf %in% c(19,20)) & !smic55 ) | (naia==year & rga=='6')) )  # TODO check year ou year-1 !
# # enfant_fip <- within(enfant_fip,{
# #                      noifam=100*ident+noidec
# #                      famille=50
# #                      kid=TRUE})
# # #                     ident=NA}) # TODO : je ne sais pas quoi mettre un NA fausse les manips suivantes 
# # famille <- rbind(famille,enfant_fip)
# # 
# # # TODO: En 2006 on peut faire ce qui suit car tous les parents fip sont déjà dans une famille
# # parent_fip <- famille[famille$noindiv %in% enfant_fip$noifam,]
# # any(enfant_fip$noifam %in% parent_fip$noindiv)
# # parent_fip <- within(parent_fip,{
# #                      noifam <- noindiv
# #                      famille <- 51
# #                      kid <- FALSE})
# # famille[famille$noindiv %in% enfant_fip$noifam,] <- parent_fip
# # # TODO quid du conjoint ?
# # dup <- duplicated(famille$noindiv)
# # table(dup)
# # 
# # table(famille$famille,useNA='ifany')
# # rm(enfant_fip,fip,parent_fip)
    
    print "extension de base"
    print fip.describe()
    base_ = concat([base, fip])
    print len(base.index)
    
    enfant_fip = subset_base(base_, famille)
    print enfant_fip.ix[enfant_fip['quelfic']=="FIP","agepf"].describe()
    
    enfant_fip = enfant_fip[(enfant_fip['quelfic']=="FIP") &
                            ((enfant_fip.agepf.isin([19,20]) & not_(enfant_fip['smic55'])) | 
                            ((enfant_fip['naia']==enfant_fip['year']-1) & (enfant_fip['rga'].astype('int')==6)))]
    
    enfant_fip['noifam'] = 100*enfant_fip['ident'] + enfant_fip['noidec']
    enfant_fip['famille'] = 50
    enfant_fip['kid'] = True
    enfant_fip['ident'] = None
    control(enfant_fip)
    famille = concat([famille, enfant_fip])
    base = concat([base, enfant_fip])

    parent_fip = famille[famille.noindiv.isin(enfant_fip.noifam.values)]
    if any(enfant_fip.noifam.isin(parent_fip.noindiv.values)): print "Doublons entre enfant_fip et parent fip !"
    parent_fip['noifam'] = parent_fip['noindiv']
    parent_fip['famille'] = 51
    parent_fip['kid'] = False
    control(parent_fip)
    
    print 'famille defore merge and clearing'
    control(famille)
    print set(famille.famille.values)
    
    famille = famille.merge(parent_fip, how='outer'); famille['famille'] = famille['famille'].astype('int')
    famille = famille.drop_duplicates(cols='noindiv', take_last=True)
    
    print 'famille after merge and clearing'
    print set(famille.famille.values)
    control(famille)
    print famille.loc[famille.noindiv.isin(enfant_fip.noifam), 'famille'].describe()
    del enfant_fip, fip, parent_fip
    
# # ##******************************************************************************************************************/
# # message('Etape 6 : non attribué')
# # non_attribue1 <- base[(!base$noindiv %in% famille$noindiv),] 
# # non_attribue1 <- subset(non_attribue1,
# #                         (quelfic!="FIP") & (m15 | (p16m20&(lien %in% c(1,2,3,4) & agepr>=35)))
# #                         )
# # # On rattache les moins de 15 ans avec la PR (on a déjà éliminé les enfants en nourrice)                         
# # non_attribue1 <- merge(pr,non_attribue1)
# # non_attribue1 <- within(non_attribue1,{
# #   famille <- ifelse(m15,61,62)
# #     kid <- TRUE })
# # 
# # rm(pr)
# # famille <- rbind(famille,non_attribue1)
# # dup <- duplicated(famille$noindiv)
# # table(dup)
# # rm(non_attribue1)
# # table(famille$famille, useNA="ifany")
# # 
# # non_attribue2 <- base[(!base$noindiv %in% famille$noindiv) & (base$quelfic!="FIP"),] 
# # non_attribue2 <- within(non_attribue2,{
# #   noifam <- 100*ident+noi # l'identifiant est celui du jeune */
# #     kid<-FALSE
# #     famille<-63})
# # 
# # famille <- rbind(famille,non_attribue2)
# # dup <- duplicated(famille$noindiv)
# # table(dup)
# # rm(non_attribue2)
# # table(famille$famille, useNA="ifany")
# # rm(base)
# # table(duplicated(famille$noifam))
    print 'Etape 6 : gestion des non attribués'
    print '    6.1 : non attribués type 1'
    non_attribue1 = subset_base(base,famille)
    non_attribue1 = non_attribue1[not_(non_attribue1['quelfic'] != 'FIP') & (non_attribue1['m15'] | 
                                    (non_attribue1['p16m20'] & (non_attribue1.lien.isin(range(1,5))) & 
                                     (non_attribue1['agepr']>=35)))]
    # On rattache les moins de 15 ans avec la PR (on a déjà éliminé les enfants en nourrice) 
    non_attribue1 = pr.merge(non_attribue1)
    control(non_attribue1)
    non_attribue1['famille'] = where(non_attribue1['m15'], 61, 62)
    non_attribue1['kid'] = True
    
    famille = concat([famille, non_attribue1])
    control(famille)
    del pr, non_attribue1

    print '    6.2 : non attribué type 2'
    non_attribue2 = base[(not_(base.noindiv.isin(famille.noindiv.values)) & (base['quelfic']!="FIP"))]
    non_attribue2['noifam'] = 100*non_attribue2['ident'] + non_attribue2['noi']
    non_attribue2['noifam'] = non_attribue2['noifam'].astype('int')
    non_attribue2['kid'] = False
    non_attribue2['famille'] = 63
    
    famille = concat([famille, non_attribue2], join='inner')
    control(famille)
    del non_attribue2
    
# # ##******************************************************************************************************************/
# # ## Sauvegarde de la table famille */  
# # 
# # # TODO nettoyer les champs qui ne servent plus à rien
# # 
# # famille <- within(famille,{
# #   idec <- paste(substr(declar1,4,11),substr(declar1,1,2),sep = '-') # TODO remove me ?
# #     chef <- (noifam == ident*100+noi)
# # })
# # table(famille$chef,useNA="ifany")
# # # On a bien autant de famille que de chef de famille 
# # 
# # famille$kid <- as.numeric(famille$kid)
# # 
# # famille <- famille[order(famille$noifam,famille$kid,!famille$chef,famille$naia,famille$naim),]
# # famille$chef <- as.numeric(famille$chef)
# # 
# # famille$rang = unsplit(lapply(split(famille$kid,famille$noifam),cumsum),famille$noifam)
# # 
# # dup <- duplicated(famille$noindiv)
# # table(dup)
# # 
# # famille$quifam[famille$chef == 1] <- 0
# # famille$quifam[(famille$chef == 0) & (famille$kid ==0)] <- 1
# # famille$quifam[famille$kid == 1] <- 1 + famille$rang[famille$kid == 1]
# # famille <- subset(famille, select = c(noindiv, quifam, noifam))
# # famille <- rename(famille, c(noifam = "idfam"))
# # 
# # length(unique(famille$idfam))
# # table(famille$quifam,useNA="ifany")
# # sum(table(famille$quifam,useNA="ifany"))
# # 
# # print(length(table(famille$noindiv)))
# # 
# # # Vérifications des duplicats dans famille (même noindiv)
# # dup <- duplicated(famille[,c("idfam","quifam")])
# # table(dup,useNA="ifany")
# # 
# # save(famille,file=famc)
# # rm(famille, indivi, enfnn)
# # gc()

    print 'Sauvegarde de la table famille'
    print '    Mise en forme finale'
    famille['idec'] = famille['declar1'].str[3:11]
    print famille['declar1'].notnull().describe()
    famille['idec'].apply(lambda x: str(x)+'-')
    famille['idec'] += famille['declar1'].str[0:2]
    famille['chef'] = (famille['noifam'] == famille['ident']*100+famille['noi'])
    famille.reset_index(inplace=True)
#     print equal(famille['declar1'], array("")).describe()
#     print equal(famille['declar1'], array('')).isnull().describe()
    print famille['idec'].isnull().describe()
    
    control(famille)
    
    print 'création de la colonne rang'  
    famille['rang'] = famille['kid'].astype('int')  
    while any(famille[(famille['rang']!=0)].duplicated(cols=['rang', 'noifam'])):
        famille["rang"][famille['rang']!=0] = where(
                                    famille[famille['rang']!=0].duplicated(cols=["rang", 'noifam']),
                                    famille["rang"][famille['rang']!=0] + 1,
                                    famille["rang"][famille['rang']!=0])
        print "nb de rangs différents", len(set(famille.rang.values))
            
    print 'création de la colonne quifam et troncature'
    famille['quifam'] = NaN
    famille['quifam'][famille['chef']==1] = 0
    famille['quifam'][(famille['chef']==0) & (famille['kid']==0)] = 1
    famille['quifam'][famille['kid']==1] = 1 + famille['rang'][famille['kid']==1]
    famille['noifam'] = famille['noifam'].astype('int')
    famille_check = famille
    famille = famille.loc[:, ['noindiv', 'quifam', 'noifam']]
    famille.columns = ['noindiv', 'quifam', 'idfam']
    print famille.head()
    
    print 'Vérifications sur famille'
    assert len(famille_check.loc[famille_check['chef'], :]) == len(set(famille.idfam.values)), 'the number of family chiefs is different from the number of families'
    assert not(any(famille.duplicated(cols=['idfam', 'quifam']))), 'there are duplicates of quifam inside a family'
    
    print 'Sauvegarde'
    save_temp(famille, name="famc", year=year)
    del famille_check, indivi, enfnn
    
if __name__ == '__main__':
    famille()