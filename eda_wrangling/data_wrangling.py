import pandas as pd
import geopandas as gpd
import os
from sqlalchemy import create_engine, text
from matplotlib.path import Path
import numpy as np
from scipy import spatial
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
import geopandas

#maximum number of rows to display
pd.options.display.max_rows = 20
engine=create_engine(f'postgresql://ds:ds@localhost/postgres', max_overflow=20)

def runQuery(sql):
    result = engine.connect().execution_options(isolation_level="AUTOCOMMIT").execute((text(sql)))
    return pd.DataFrame(result.fetchall(), columns=result.keys())

def setup():
    georef_file = os.path.abspath("./data/bogota/CNPV2018_MGN_A2_11.CSV")
    vivienda_file = os.path.abspath("./data/bogota/CNPV2018_1VIV_A2_11.CSV")
    personas_file = os.path.abspath("./data/bogota/CNPV2018_5PER_A2_11.CSV")

    return runQuery("""
    CREATE TABLE georef (U_DPTO integer, U_MPIO integer, UA_CLASE integer, UA1_LOCALIDAD integer, U_SECT_RUR integer,
       U_SECC_RUR integer, UA2_CPOB integer, U_SECT_URB integer, U_SECC_URB integer, U_MZA integer,
       U_EDIFICA integer, COD_ENCUESTAS integer, U_VIVIENDA integer);
    CREATE TABLE vivienda (TIPO_REG integer, U_DPTO integer, U_MPIO integer, UA_CLASE integer, U_EDIFICA integer,
       COD_ENCUESTAS integer, U_VIVIENDA integer, UVA_ESTATER integer, UVA1_TIPOTER decimal,
       UVA2_CODTER decimal, UVA_ESTA_AREAPROT integer, UVA1_COD_AREAPROT decimal,
       UVA_USO_UNIDAD integer, V_TIPO_VIV decimal, V_CON_OCUP decimal, V_TOT_HOG decimal,
       V_MAT_PARED decimal, V_MAT_PISO decimal, VA_EE decimal, VA1_ESTRATO decimal, VB_ACU decimal, VC_ALC decimal,
       VD_GAS decimal, VE_RECBAS decimal, VE1_QSEM decimal, VF_INTERNET decimal, V_TIPO_SERSA decimal,
       L_TIPO_INST decimal, L_EXISTEHOG decimal, L_TOT_PERL decimal);
    CREATE TABLE personas (TIPO_REG integer, U_DPTO integer, U_MPIO integer, UA_CLASE integer, U_EDIFICA integer,
       COD_ENCUESTAS integer, U_VIVIENDA integer, P_NROHOG decimal, P_NRO_PER integer, P_SEXO integer,
       P_EDADR integer, P_PARENTESCOR decimal, PA1_GRP_ETNIC integer, PA11_COD_ETNIA decimal,
       PA12_CLAN decimal, PA21_COD_VITSA decimal, PA22_COD_KUMPA decimal, PA_HABLA_LENG decimal,
       PA1_ENTIENDE decimal, PB_OTRAS_LENG decimal, PB1_QOTRAS_LENG decimal, PA_LUG_NAC integer,
       PA_VIVIA_5ANOS decimal, PA_VIVIA_1ANO decimal, P_ENFERMO decimal, P_QUEHIZO_PPAL decimal,
       PA_LO_ATENDIERON decimal, PA1_CALIDAD_SERV decimal, CONDICION_FISICA decimal,
       P_ALFABETA decimal, PA_ASISTENCIA decimal, P_NIVEL_ANOSR decimal, P_TRABAJO decimal,
       P_EST_CIVIL decimal, PA_HNV decimal, PA1_THNV decimal, PA2_HNVH decimal, PA3_HNVM decimal, PA_HNVS decimal,
       PA1_THSV decimal, PA2_HSVH decimal, PA3_HSVM decimal, PA_HFC decimal, PA1_THFC decimal, PA2_HFCH decimal,
       PA3_HFCM decimal, PA_UHNV decimal, PA1_MES_UHNV decimal, PA2_ANO_UHNV decimal);
    COPY georef FROM '""" + georef_file + """' WITH (format csv, header true, delimiter ',');
    COPY vivienda FROM '""" + vivienda_file + """' WITH (format csv, header true, delimiter ',');
    COPY personas FROM '""" + personas_file + """' WITH (format csv, header true, delimiter ',');
    SELECT * FROM georef LIMIT(5);
    """)
    
def cleanup():
    runQuery("""
    DROP TABLE georef CASCADE;
    DROP TABLE vivienda CASCADE;
    DROP TABLE personas CASCADE;
    SELECT 0 WHERE FALSE; -- prevents SQLAlchemy from throwing an error
    """)

def explode(df, lst_cols, fill_value='', preserve_index=False):
    # make sure `lst_cols` is list-alike
    if (lst_cols is not None
            and len(lst_cols) > 0
            and not isinstance(lst_cols, (list, tuple, np.ndarray, pd.Series))):
        lst_cols = [lst_cols]
    # all columns except `lst_cols`
    idx_cols = df.columns.difference(lst_cols)
    # calculate lengths of lists
    lens = df[lst_cols[0]].str.len()
    # preserve original index values
    idx = np.repeat(df.index.values, lens)
    # create "exploded" DF
    res = (pd.DataFrame({
        col: np.repeat(df[col].values, lens)
        for col in idx_cols},
        index=idx)
           .assign(**{col: np.concatenate(df.loc[lens > 0, col].values)
                      for col in lst_cols}))
    # append those rows that have empty lists
    if (lens == 0).any():
        # at least one list in cells is empty
        res = (res.append(df.loc[lens == 0, idx_cols], sort=False)
               .fillna(fill_value))
    # revert the original index order
    res = res.sort_index()
    # reset index if requested
    if not preserve_index:
        res = res.reset_index(drop=True)
    return res

def points_in_distance(blocks, points, column_name, distance_upper):
    blocks_array = blocks[['MANZ_CCNCT']].values
    lat_lng_blocks_array = blocks[['LAT','LNG']].values

    lat_lng_points_array = points[['LAT','LNG']].values

    distances = spatial.cKDTree(lat_lng_blocks_array).query(lat_lng_points_array, 500, p=1, distance_upper_bound=distance_upper, n_jobs=-1)

    dist=[]
    index =[]
    tok =[]
    for x,y in zip(distances[0],distances[1]):
        del_index = np.where(x== np.inf)
    
        dist_cleaned = np.delete(x, del_index[0])
        index_cleaned= np.delete(y, del_index[0])

        dist.append(dist_cleaned)
        index.append(index_cleaned)
        tok.append(blocks_array[index_cleaned])
    
    dist=np.array(dist)
    index=np.array(index)
    tok=np.array(tok)

    points_blocks = points.copy()
    points_blocks['MANZ_CCNCT'] = tok
    points_blocks = explode(points_blocks, ['MANZ_CCNCT'])
    points_blocks = points_blocks[points_blocks['MANZ_CCNCT']!='']
    points_per_block = pd.DataFrame(points_blocks.groupby('MANZ_CCNCT').count()['LAT']).reset_index()
    points_per_block.columns = ['MANZ_CCNCT', column_name]
    output = pd.merge(blocks, points_per_block, how='left', on='MANZ_CCNCT')
    output[column_name].fillna(0, inplace=True)
    return output

def locality_in_distance(blocks, points, column_name, distance_upper):
    blocks_array = blocks[['MANZ_CCNCT']].values
    lat_lng_blocks_array = blocks[['LAT','LNG']].values
    
    points.dropna(subset=['localidad_calculada'], inplace=True)
    lat_lng_points_array = points[['LAT','LNG']].values

    distances = spatial.cKDTree(lat_lng_blocks_array).query(lat_lng_points_array, 1, p=1, distance_upper_bound=distance_upper, n_jobs=-1)

    dist=[]
    index =[]
    tok =[]
    for x,y in zip(distances[0],distances[1]):
        del_index = np.where(x== np.inf)
    
        dist_cleaned = np.delete(x, del_index[0])
        index_cleaned= np.delete(y, del_index[0])

        dist.append(dist_cleaned)
        index.append(index_cleaned)
        tok.append(blocks_array[index_cleaned])
    
    dist=np.array(dist)
    index=np.array(index)
    tok=np.array(tok)

    points_blocks = points.copy()
    points_blocks['MANZ_CCNCT'] = tok
    points_blocks = points_blocks[points_blocks['MANZ_CCNCT']!='']
    points_per_block = points_blocks[['MANZ_CCNCT','localidad_calculada']]
    points_per_block.columns = ['MANZ_CCNCT', column_name]
    output = pd.merge(blocks, points_per_block, how='left', on='MANZ_CCNCT')
    return output

setup()

union = runQuery("""
with str_columns as (
select LPAD(u_dpto::text, 2, '0') u_dpto,
LPAD(u_mpio::text, 3, '0') u_mpio,
LPAD(ua_clase::text, 1, '0') ua_clase,
LPAD(u_sect_rur::text, 3, '0') u_sect_rur,
LPAD(u_secc_rur::text, 2, '0') u_secc_rur,
LPAD(ua2_cpob::text, 3, '0') ua2_cpob,
LPAD(u_sect_urb::text, 4, '0') u_sect_urb,
LPAD(u_secc_urb::text, 2, '0') u_secc_urb,
LPAD(u_mza::text, 2, '0') u_mza,
cod_encuestas
from georef
)
,dane_encuestas as (
select
concat(u_dpto,u_mpio,ua_clase,u_sect_rur,u_secc_rur,ua2_cpob,u_sect_urb,u_secc_urb,u_mza) as cod_dane,
cod_encuestas
from str_columns
)
,tabla_viviendas as (
select
cod_dane cod_dane_viv,
sum(case when UVA_USO_UNIDAD = 1 Then 1 end) NUM_UVA_USO_UNIDAD_1,
sum(case when UVA_USO_UNIDAD = 2 Then 1 end) NUM_UVA_USO_UNIDAD_2,
sum(case when UVA_USO_UNIDAD = 3 Then 1 end) NUM_UVA_USO_UNIDAD_3,
sum(case when UVA_USO_UNIDAD = 4 Then 1 end) NUM_UVA_USO_UNIDAD_4,
sum(case when V_TIPO_VIV = 1 Then 1 end) NUM_V_TIPO_VIV_1,
sum(case when V_TIPO_VIV = 2 Then 1 end) NUM_V_TIPO_VIV_2,
sum(case when V_TIPO_VIV = 3 Then 1 end) NUM_V_TIPO_VIV_3,
sum(case when V_TIPO_VIV = 4 Then 1 end) NUM_V_TIPO_VIV_4,
sum(case when V_TIPO_VIV = 5 Then 1 end) NUM_V_TIPO_VIV_5,
sum(case when V_TIPO_VIV = 6 Then 1 end) NUM_V_TIPO_VIV_6,
sum(case when V_CON_OCUP = 1 Then 1 end) NUM_V_CON_OCUP_1,
sum(case when V_CON_OCUP = 2 Then 1 end) NUM_V_CON_OCUP_2,
sum(case when V_CON_OCUP = 3 Then 1 end) NUM_V_CON_OCUP_3,
sum(case when V_CON_OCUP = 4 Then 1 end) NUM_V_CON_OCUP_4,
sum(case when V_TOT_HOG = 0 Then 1 end) NUM_V_TOT_HOG_0,
sum(case when V_TOT_HOG = 1 Then 1 end) NUM_V_TOT_HOG_1,
sum(case when V_TOT_HOG = 2 Then 1 end) NUM_V_TOT_HOG_2,
sum(case when V_TOT_HOG = 3 Then 1 end) NUM_V_TOT_HOG_3,
sum(case when V_TOT_HOG = 4 Then 1 end) NUM_V_TOT_HOG_4,
sum(case when V_TOT_HOG = 5 Then 1 end) NUM_V_TOT_HOG_5,
sum(case when V_TOT_HOG = 6 Then 1 end) NUM_V_TOT_HOG_6,
sum(case when V_TOT_HOG = 7 Then 1 end) NUM_V_TOT_HOG_7,
sum(case when V_TOT_HOG = 8 Then 1 end) NUM_V_TOT_HOG_8,
sum(case when V_TOT_HOG = 9 Then 1 end) NUM_V_TOT_HOG_9,
sum(case when V_TOT_HOG = 10 Then 1 end) NUM_V_TOT_HOG_10,
sum(case when V_TOT_HOG = 11 Then 1 end) NUM_V_TOT_HOG_11,
sum(case when V_TOT_HOG = 12 Then 1 end) NUM_V_TOT_HOG_12,
sum(case when V_TOT_HOG = 13 Then 1 end) NUM_V_TOT_HOG_13,
sum(case when V_TOT_HOG = 14 Then 1 end) NUM_V_TOT_HOG_14,
sum(case when V_TOT_HOG = 15 Then 1 end) NUM_V_TOT_HOG_15,
sum(case when V_TOT_HOG = 16 Then 1 end) NUM_V_TOT_HOG_16,
sum(case when V_TOT_HOG = 17 Then 1 end) NUM_V_TOT_HOG_17,
sum(case when V_TOT_HOG = 18 Then 1 end) NUM_V_TOT_HOG_18,
sum(case when V_TOT_HOG = 19 Then 1 end) NUM_V_TOT_HOG_19,
sum(case when V_TOT_HOG = 20 Then 1 end) NUM_V_TOT_HOG_20,
sum(case when V_TOT_HOG = 21 Then 1 end) NUM_V_TOT_HOG_21,
sum(case when V_TOT_HOG = 22 Then 1 end) NUM_V_TOT_HOG_22,
sum(case when V_TOT_HOG = 23 Then 1 end) NUM_V_TOT_HOG_23,
sum(case when V_TOT_HOG = 24 Then 1 end) NUM_V_TOT_HOG_24,
sum(case when V_TOT_HOG = 25 Then 1 end) NUM_V_TOT_HOG_25,
sum(case when V_MAT_PARED = 1 Then 1 end) NUM_V_MAT_PARED_1,
sum(case when V_MAT_PARED = 2 Then 1 end) NUM_V_MAT_PARED_2,
sum(case when V_MAT_PARED = 3 Then 1 end) NUM_V_MAT_PARED_3,
sum(case when V_MAT_PARED = 4 Then 1 end) NUM_V_MAT_PARED_4,
sum(case when V_MAT_PARED = 5 Then 1 end) NUM_V_MAT_PARED_5,
sum(case when V_MAT_PARED = 6 Then 1 end) NUM_V_MAT_PARED_6,
sum(case when V_MAT_PARED = 7 Then 1 end) NUM_V_MAT_PARED_7,
sum(case when V_MAT_PARED = 8 Then 1 end) NUM_V_MAT_PARED_8,
sum(case when V_MAT_PARED = 9 Then 1 end) NUM_V_MAT_PARED_9,
sum(case when V_MAT_PISO = 1 Then 1 end) NUM_V_MAT_PISO_1,
sum(case when V_MAT_PISO = 2 Then 1 end) NUM_V_MAT_PISO_2,
sum(case when V_MAT_PISO = 3 Then 1 end) NUM_V_MAT_PISO_3,
sum(case when V_MAT_PISO = 4 Then 1 end) NUM_V_MAT_PISO_4,
sum(case when V_MAT_PISO = 5 Then 1 end) NUM_V_MAT_PISO_5,
sum(case when V_MAT_PISO = 6 Then 1 end) NUM_V_MAT_PISO_6,
sum(case when VA_EE = 1 Then 1 end) NUM_VA_EE_1,
sum(case when VA_EE = 2 Then 1 end) NUM_VA_EE_2,
sum(case when VA1_ESTRATO = 0 Then 1 end) NUM_VA1_ESTRATO_0,
sum(case when VA1_ESTRATO = 1 Then 1 end) NUM_VA1_ESTRATO_1,
sum(case when VA1_ESTRATO = 2 Then 1 end) NUM_VA1_ESTRATO_2,
sum(case when VA1_ESTRATO = 3 Then 1 end) NUM_VA1_ESTRATO_3,
sum(case when VA1_ESTRATO = 4 Then 1 end) NUM_VA1_ESTRATO_4,
sum(case when VA1_ESTRATO = 5 Then 1 end) NUM_VA1_ESTRATO_5,
sum(case when VA1_ESTRATO = 6 Then 1 end) NUM_VA1_ESTRATO_6,
sum(case when VB_ACU = 1 Then 1 end) NUM_VB_ACU_1,
sum(case when VB_ACU = 2 Then 1 end) NUM_VB_ACU_2,
sum(case when VC_ALC = 1 Then 1 end) NUM_VC_ALC_1,
sum(case when VC_ALC = 2 Then 1 end) NUM_VC_ALC_2,
sum(case when VD_GAS = 1 Then 1 end) NUM_VD_GAS_1,
sum(case when VD_GAS = 2 Then 1 end) NUM_VD_GAS_2,
sum(case when VD_GAS = 9 Then 1 end) NUM_VD_GAS_9,
sum(case when VE_RECBAS = 1 Then 1 end) NUM_VE_RECBAS_1,
sum(case when VE_RECBAS = 2 Then 1 end) NUM_VE_RECBAS_2,
sum(case when VE_RECBAS = 9 Then 1 end) NUM_VE_RECBAS_9,
sum(case when VE1_QSEM = 1 Then 1 end) NUM_VE1_QSEM_1,
sum(case when VE1_QSEM = 2 Then 1 end) NUM_VE1_QSEM_2,
sum(case when VE1_QSEM = 3 Then 1 end) NUM_VE1_QSEM_3,
sum(case when VE1_QSEM = 4 Then 1 end) NUM_VE1_QSEM_4,
sum(case when VE1_QSEM = 5 Then 1 end) NUM_VE1_QSEM_5,
sum(case when VE1_QSEM = 6 Then 1 end) NUM_VE1_QSEM_6,
sum(case when VE1_QSEM = 7 Then 1 end) NUM_VE1_QSEM_7,
sum(case when VE1_QSEM = 8 Then 1 end) NUM_VE1_QSEM_8,
sum(case when VE1_QSEM = 9 Then 1 end) NUM_VE1_QSEM_9,
sum(case when VF_INTERNET = 1 Then 1 end) NUM_VF_INTERNET_1,
sum(case when VF_INTERNET = 2 Then 1 end) NUM_VF_INTERNET_2,
sum(case when V_TIPO_SERSA = 1 Then 1 end) NUM_V_TIPO_SERSA_1,
sum(case when V_TIPO_SERSA = 2 Then 1 end) NUM_V_TIPO_SERSA_2,
sum(case when V_TIPO_SERSA = 3 Then 1 end) NUM_V_TIPO_SERSA_3,
sum(case when V_TIPO_SERSA = 4 Then 1 end) NUM_V_TIPO_SERSA_4,
sum(case when V_TIPO_SERSA = 5 Then 1 end) NUM_V_TIPO_SERSA_5,
sum(case when V_TIPO_SERSA = 6 Then 1 end) NUM_V_TIPO_SERSA_6,
sum(case when L_TIPO_INST = 1 Then 1 end) NUM_L_TIPO_INST_1,
sum(case when L_TIPO_INST = 2 Then 1 end) NUM_L_TIPO_INST_2,
sum(case when L_TIPO_INST = 3 Then 1 end) NUM_L_TIPO_INST_3,
sum(case when L_TIPO_INST = 4 Then 1 end) NUM_L_TIPO_INST_4,
sum(case when L_TIPO_INST = 5 Then 1 end) NUM_L_TIPO_INST_5,
sum(case when L_TIPO_INST = 6 Then 1 end) NUM_L_TIPO_INST_6,
sum(case when L_TIPO_INST = 7 Then 1 end) NUM_L_TIPO_INST_7,
sum(case when L_TIPO_INST = 8 Then 1 end) NUM_L_TIPO_INST_8,
sum(case when L_TIPO_INST = 9 Then 1 end) NUM_L_TIPO_INST_9,
sum(case when L_TIPO_INST = 10 Then 1 end) NUM_L_TIPO_INST_10,
sum(case when L_TIPO_INST = 11 Then 1 end) NUM_L_TIPO_INST_11,
sum(case when L_TIPO_INST = 12 Then 1 end) NUM_L_TIPO_INST_12,
sum(case when L_TIPO_INST = 13 Then 1 end) NUM_L_TIPO_INST_13,
sum(case when L_EXISTEHOG = 1 Then 1 end) NUM_L_EXISTEHOG_1,
sum(case when L_EXISTEHOG = 2 Then 1 end) NUM_L_EXISTEHOG_2,
sum(case when L_EXISTEHOG = 9 Then 1 end) NUM_L_EXISTEHOG_9
from vivienda viv
left join dane_encuestas dan
on viv.cod_encuestas = dan.cod_encuestas
group by 1
)
,tabla_personas as (
select
cod_dane cod_dane_per,
sum(case when P_SEXO = 1 Then 1 end) NUM_P_SEXO_1,
sum(case when P_SEXO = 2 Then 1 end) NUM_P_SEXO_2,
sum(case when P_EDADR = 1 Then 1 end) NUM_P_EDADR_1,
sum(case when P_EDADR = 2 Then 1 end) NUM_P_EDADR_2,
sum(case when P_EDADR = 3 Then 1 end) NUM_P_EDADR_3,
sum(case when P_EDADR = 4 Then 1 end) NUM_P_EDADR_4,
sum(case when P_EDADR = 5 Then 1 end) NUM_P_EDADR_5,
sum(case when P_EDADR = 6 Then 1 end) NUM_P_EDADR_6,
sum(case when P_EDADR = 7 Then 1 end) NUM_P_EDADR_7,
sum(case when P_EDADR = 8 Then 1 end) NUM_P_EDADR_8,
sum(case when P_EDADR = 9 Then 1 end) NUM_P_EDADR_9,
sum(case when P_EDADR = 10 Then 1 end) NUM_P_EDADR_10,
sum(case when P_EDADR = 11 Then 1 end) NUM_P_EDADR_11,
sum(case when P_EDADR = 12 Then 1 end) NUM_P_EDADR_12,
sum(case when P_EDADR = 13 Then 1 end) NUM_P_EDADR_13,
sum(case when P_EDADR = 14 Then 1 end) NUM_P_EDADR_14,
sum(case when P_EDADR = 15 Then 1 end) NUM_P_EDADR_15,
sum(case when P_EDADR = 16 Then 1 end) NUM_P_EDADR_16,
sum(case when P_EDADR = 17 Then 1 end) NUM_P_EDADR_17,
sum(case when P_EDADR = 18 Then 1 end) NUM_P_EDADR_18,
sum(case when P_EDADR = 19 Then 1 end) NUM_P_EDADR_19,
sum(case when P_EDADR = 20 Then 1 end) NUM_P_EDADR_20,
sum(case when P_EDADR = 21 Then 1 end) NUM_P_EDADR_21,
sum(case when PA_LUG_NAC = 1 Then 1 end) NUM_PA_LUG_NAC_1,
sum(case when PA_LUG_NAC = 2 Then 1 end) NUM_PA_LUG_NAC_2,
sum(case when PA_LUG_NAC = 3 Then 1 end) NUM_PA_LUG_NAC_3,
sum(case when PA_LUG_NAC = 9 Then 1 end) NUM_PA_LUG_NAC_9,
sum(case when PA_VIVIA_5ANOS = 1 Then 1 end) NUM_PA_VIVIA_5ANOS_1,
sum(case when PA_VIVIA_5ANOS = 2 Then 1 end) NUM_PA_VIVIA_5ANOS_2,
sum(case when PA_VIVIA_5ANOS = 3 Then 1 end) NUM_PA_VIVIA_5ANOS_3,
sum(case when PA_VIVIA_5ANOS = 4 Then 1 end) NUM_PA_VIVIA_5ANOS_4,
sum(case when PA_VIVIA_5ANOS = 9 Then 1 end) NUM_PA_VIVIA_5ANOS_9,
sum(case when PA_VIVIA_1ANO = 1 Then 1 end) NUM_PA_VIVIA_1ANO_1,
sum(case when PA_VIVIA_1ANO = 2 Then 1 end) NUM_PA_VIVIA_1ANO_2,
sum(case when PA_VIVIA_1ANO = 3 Then 1 end) NUM_PA_VIVIA_1ANO_3,
sum(case when PA_VIVIA_1ANO = 4 Then 1 end) NUM_PA_VIVIA_1ANO_4,
sum(case when PA_VIVIA_1ANO = 9 Then 1 end) NUM_PA_VIVIA_1ANO_9,
sum(case when P_ENFERMO = 1 Then 1 end) NUM_P_ENFERMO_1,
sum(case when P_ENFERMO = 2 Then 1 end) NUM_P_ENFERMO_2,
sum(case when P_ENFERMO = 9 Then 1 end) NUM_P_ENFERMO_9,
sum(case when P_QUEHIZO_PPAL = 1 Then 1 end) NUM_P_QUEHIZO_PPAL_1,
sum(case when P_QUEHIZO_PPAL = 2 Then 1 end) NUM_P_QUEHIZO_PPAL_2,
sum(case when P_QUEHIZO_PPAL = 3 Then 1 end) NUM_P_QUEHIZO_PPAL_3,
sum(case when P_QUEHIZO_PPAL = 4 Then 1 end) NUM_P_QUEHIZO_PPAL_4,
sum(case when P_QUEHIZO_PPAL = 5 Then 1 end) NUM_P_QUEHIZO_PPAL_5,
sum(case when P_QUEHIZO_PPAL = 6 Then 1 end) NUM_P_QUEHIZO_PPAL_6,
sum(case when P_QUEHIZO_PPAL = 7 Then 1 end) NUM_P_QUEHIZO_PPAL_7,
sum(case when P_QUEHIZO_PPAL = 8 Then 1 end) NUM_P_QUEHIZO_PPAL_8,
sum(case when P_QUEHIZO_PPAL = 9 Then 1 end) NUM_P_QUEHIZO_PPAL_9,
sum(case when PA_LO_ATENDIERON = 1 Then 1 end) NUM_PA_LO_ATENDIERON_1,
sum(case when PA_LO_ATENDIERON = 2 Then 1 end) NUM_PA_LO_ATENDIERON_2,
sum(case when PA_LO_ATENDIERON = 9 Then 1 end) NUM_PA_LO_ATENDIERON_9,
sum(case when PA1_CALIDAD_SERV = 1 Then 1 end) NUM_PA1_CALIDAD_SERV_1,
sum(case when PA1_CALIDAD_SERV = 2 Then 1 end) NUM_PA1_CALIDAD_SERV_2,
sum(case when PA1_CALIDAD_SERV = 3 Then 1 end) NUM_PA1_CALIDAD_SERV_3,
sum(case when PA1_CALIDAD_SERV = 4 Then 1 end) NUM_PA1_CALIDAD_SERV_4,
sum(case when PA1_CALIDAD_SERV = 9 Then 1 end) NUM_PA1_CALIDAD_SERV_9,
sum(case when CONDICION_FISICA = 1 Then 1 end) NUM_CONDICION_FISICA_1,
sum(case when CONDICION_FISICA = 2 Then 1 end) NUM_CONDICION_FISICA_2,
sum(case when CONDICION_FISICA = 9 Then 1 end) NUM_CONDICION_FISICA_9,
sum(case when PA_ASISTENCIA = 1 Then 1 end) NUM_PA_ASISTENCIA_1,
sum(case when PA_ASISTENCIA = 2 Then 1 end) NUM_PA_ASISTENCIA_2,
sum(case when PA_ASISTENCIA = 9 Then 1 end) NUM_PA_ASISTENCIA_9,
sum(case when P_NIVEL_ANOSR = 1 Then 1 end) NUM_P_NIVEL_ANOSR_1,
sum(case when P_NIVEL_ANOSR = 2 Then 1 end) NUM_P_NIVEL_ANOSR_2,
sum(case when P_NIVEL_ANOSR = 3 Then 1 end) NUM_P_NIVEL_ANOSR_3,
sum(case when P_NIVEL_ANOSR = 4 Then 1 end) NUM_P_NIVEL_ANOSR_4,
sum(case when P_NIVEL_ANOSR = 5 Then 1 end) NUM_P_NIVEL_ANOSR_5,
sum(case when P_NIVEL_ANOSR = 6 Then 1 end) NUM_P_NIVEL_ANOSR_6,
sum(case when P_NIVEL_ANOSR = 7 Then 1 end) NUM_P_NIVEL_ANOSR_7,
sum(case when P_NIVEL_ANOSR = 8 Then 1 end) NUM_P_NIVEL_ANOSR_8,
sum(case when P_NIVEL_ANOSR = 9 Then 1 end) NUM_P_NIVEL_ANOSR_9,
sum(case when P_NIVEL_ANOSR = 10 Then 1 end) NUM_P_NIVEL_ANOSR_10,
sum(case when P_NIVEL_ANOSR = 99 Then 1 end) NUM_P_NIVEL_ANOSR_99,
sum(case when P_TRABAJO = 0 Then 1 end) NUM_P_TRABAJO_0,
sum(case when P_TRABAJO = 1 Then 1 end) NUM_P_TRABAJO_1,
sum(case when P_TRABAJO = 2 Then 1 end) NUM_P_TRABAJO_2,
sum(case when P_TRABAJO = 3 Then 1 end) NUM_P_TRABAJO_3,
sum(case when P_TRABAJO = 4 Then 1 end) NUM_P_TRABAJO_4,
sum(case when P_TRABAJO = 5 Then 1 end) NUM_P_TRABAJO_5,
sum(case when P_TRABAJO = 6 Then 1 end) NUM_P_TRABAJO_6,
sum(case when P_TRABAJO = 7 Then 1 end) NUM_P_TRABAJO_7,
sum(case when P_TRABAJO = 8 Then 1 end) NUM_P_TRABAJO_8,
sum(case when P_TRABAJO = 9 Then 1 end) NUM_P_TRABAJO_9,
sum(case when P_EST_CIVIL = 1 Then 1 end) NUM_P_EST_CIVIL_1,
sum(case when P_EST_CIVIL = 2 Then 1 end) NUM_P_EST_CIVIL_2,
sum(case when P_EST_CIVIL = 3 Then 1 end) NUM_P_EST_CIVIL_3,
sum(case when P_EST_CIVIL = 4 Then 1 end) NUM_P_EST_CIVIL_4,
sum(case when P_EST_CIVIL = 5 Then 1 end) NUM_P_EST_CIVIL_5,
sum(case when P_EST_CIVIL = 6 Then 1 end) NUM_P_EST_CIVIL_6,
sum(case when P_EST_CIVIL = 7 Then 1 end) NUM_P_EST_CIVIL_7,
sum(case when P_EST_CIVIL = 9 Then 1 end) NUM_P_EST_CIVIL_9,
sum(case when P_ENFERMO = 1 or CONDICION_FISICA = 1 then 1 end) NUM_HEALTH_PHYSICAL
from personas per
left join dane_encuestas dan
on per.cod_encuestas = dan.cod_encuestas
group by 1
)
select tv.*, tp.*
from tabla_viviendas tv
full outer join tabla_personas tp
on tv.cod_dane_viv = tp.cod_dane_per
""")
union.drop("cod_dane_per", axis=1, inplace=True)
union.rename(columns={"cod_dane_viv":"cod_dane"}, inplace=True)

path_demographic = './data/dane_blocks/{}'.format
blocks = gpd.GeoDataFrame.from_file(path_demographic('MGN_URB_MANZANA.shp'))
blocks = blocks[~blocks.geometry.isna()]
blocks = blocks[blocks.MPIO_CCDGO == "11001"]

path_ciclovia = './data/ciclovia/{}'.format
ciclovia = gpd.GeoDataFrame.from_file(path_ciclovia('ciclovia.shp'))

path_senior = './data/senior_sports/{}'.format
senior_sports = gpd.GeoDataFrame.from_file(path_senior('Envejecimiento_Activo_y_Feliz.shp'))
senior_sports = senior_sports.to_crs(epsg='4326')
senior_sports['LAT'] = senior_sports['geometry'].centroid.y
senior_sports['LNG'] = senior_sports['geometry'].centroid.x

path_women = './data/women_sports/{}'.format
women_sports = gpd.GeoDataFrame.from_file(path_women('ParticipacionDeportiva.shp'))
women_sports['LAT'] = women_sports['geometry'].centroid.y
women_sports['LNG'] = women_sports['geometry'].centroid.x

path_soccer = './data/soccer_fields/{}'.format
soccer_fields = gpd.GeoDataFrame.from_file(path_soccer('Canchas.shp'))
soccer_fields = soccer_fields.to_crs(epsg='4326')
soccer_fields['LAT'] = soccer_fields['geometry'].centroid.y
soccer_fields['LNG'] = soccer_fields['geometry'].centroid.x

path_public_space = './data/public_space/{}'.format
urban_parks = gpd.GeoDataFrame.from_file(path_public_space('Parques.shp'))
urban_parks = urban_parks[~urban_parks.geometry.isna()]
urban_parks = urban_parks.to_crs(epsg='4326')
urban_parks['LAT'] = urban_parks['geometry'].centroid.y
urban_parks['LNG'] = urban_parks['geometry'].centroid.x
urban_parks = urban_parks[urban_parks.Shape_Area > 2000]

path_equipment = './data/Equipamientos/{}'.format
sports_spaces = gpd.GeoDataFrame.from_file(path_equipment('Deportivo.shp'))
sports_spaces = sports_spaces[~sports_spaces.geometry.isna()]
sports_spaces = sports_spaces.to_crs(epsg='4326')

health_spaces = gpd.GeoDataFrame.from_file(path_equipment('Salud.shp'))
health_spaces = health_spaces[~health_spaces.geometry.isna()]
health_spaces = health_spaces.to_crs(epsg='4326')

path_restaurants = './data/restaurants_data/{}'.format
restaurants = pd.read_csv(path_restaurants("rest_location.csv"))
healthy_restaurants = restaurants[restaurants.CATEGORY == 'Saludable']
unhealthy_restaurants = restaurants[restaurants.CATEGORY == 'No saludable']
unhealthy_gpdf = geopandas.GeoDataFrame(
    unhealthy_restaurants, geometry=geopandas.points_from_xy(unhealthy_restaurants.LNG, unhealthy_restaurants.LAT))

path_demographic = './data/population_businesses/{}'.format
businesses = gpd.GeoDataFrame.from_file(path_demographic('Empresas.shp'))
businesses = businesses[~businesses.geometry.isna()]
businesses = businesses.to_crs(epsg='4326')
drinking_places = businesses[businesses.CADENA == 'Expendio de bebidas alcoh¢licas para el consumo dentro del establecimiento']
drinking_places['LAT'] = drinking_places['geometry'].centroid.y
drinking_places['LNG'] = drinking_places['geometry'].centroid.x

blocks = pd.merge(blocks, union, how='left', left_on='MANZ_CCNCT', right_on='cod_dane')

localities_polygons = [list(women_sports.geometry.exterior[row_id].coords) for row_id in range(women_sports.shape[0])]

block_centroids = np.vstack((blocks['geometry'].centroid.x,blocks['geometry'].centroid.y)).T
blocks['LAT'] = block_centroids[:,1]
blocks['LNG'] = block_centroids[:,0]

for i in range(len(localities_polygons)):
    p = Path(localities_polygons[i]) 
    grid = p.contains_points(block_centroids)
    blocks.loc[grid,"localidad_calculada"] = women_sports["Localidad"][i]
    blocks.loc[grid,"w_bicycle_usage"] = women_sports["P_MujerBic"][i]
    blocks.loc[grid,"m_bicycle_usage"] = women_sports["P_HombreBi"][i]
    blocks.loc[grid,"w_sports_per"] = women_sports["P_MujerDep"][i]
    blocks.loc[grid,"m_sports_per"] = women_sports["P_HombreDe"][i]


blocks = points_in_distance(blocks, senior_sports, 'SENIOR_SPORTS_CENTERS', 0.00445)
blocks = points_in_distance(blocks, soccer_fields, 'SOCCER_FIELDS', 0.00445)
blocks = points_in_distance(blocks, urban_parks, 'URBAN_PARKS', 0.00445)
blocks = points_in_distance(blocks, healthy_restaurants, 'HEALTHY_RESTAURANTS', 0.00445)
blocks = points_in_distance(blocks, unhealthy_restaurants, 'UNHEALTHY_RESTAURANTS', 0.00445)
blocks = points_in_distance(blocks, drinking_places, 'DRINKING_PLACES', 0.00445)
blocks = locality_in_distance(blocks, blocks, 'LOCALITY_CENTROID', 0.0445)
blocks.loc[(blocks.localidad_calculada.isna()),'localidad_calculada'] = blocks.loc[(blocks.localidad_calculada.isna()),'LOCALITY_CENTROID']
blocks.drop('LOCALITY_CENTROID', axis=1, inplace=True)
blocks.localidad_calculada = blocks.localidad_calculada.astype(int)
localities = pd.read_csv("./data/bogota/localities_info.csv")
localities.columns = ['locality_id', 'locality_name', 'locality_codes', 'locality_area', 'locality_population', 'locality_density']
blocks = pd.merge(blocks, localities, how='left', left_on='localidad_calculada', right_on='locality_id')
blocks.drop('locality_id', axis=1, inplace=True)
blocks['MANZ_POPULATION'] = blocks[['num_p_sexo_1','num_p_sexo_2']].sum(axis=1)
blocks['ESTRATO'] = blocks[['num_va1_estrato_0','num_va1_estrato_1',
                            'num_va1_estrato_2','num_va1_estrato_3',
                            'num_va1_estrato_4','num_va1_estrato_5',
                            'num_va1_estrato_6']].idxmax(axis=1)

blocks.loc[~(blocks.ESTRATO.isna()),'ESTRATO'] = blocks.loc[~(blocks.ESTRATO.isna()),'ESTRATO'].apply(lambda x: x.split("_")[3])
blocks.loc[(blocks.MANZ_POPULATION.isna() | blocks.MANZ_POPULATION == 0), 'ESTRATO'] = 'INHABITADA'


blocks['PERC_HEALTH_PROBLEMS'] = blocks['num_p_enfermo_1']/blocks['MANZ_POPULATION']
blocks['PERC_TRADITIONAL_MEDICINE'] = blocks[['num_p_quehizo_ppal_1','num_p_quehizo_ppal_2']].sum(axis=1)/blocks['num_p_enfermo_1']
blocks['PERC_PHYSICAL_PROBLEMS'] = blocks['num_condicion_fisica_1']/blocks['MANZ_POPULATION']
blocks['PERC_ATENTION'] = blocks['num_pa_lo_atendieron_1']/blocks[['num_pa_lo_atendieron_1','num_pa_lo_atendieron_2','num_pa_lo_atendieron_9']].sum(axis=1)
blocks['PERC_NO_HEALTH_CONDITIONS'] = 1 - blocks['num_health_physical']/blocks['MANZ_POPULATION']

scaler = MinMaxScaler()
blocks['DRINKING_PLACES_STANDARD'] = scaler.fit_transform(blocks['DRINKING_PLACES'].values.reshape(-1,1))
scaler = MinMaxScaler()
blocks['PARKS_STANDARD'] = scaler.fit_transform(blocks['URBAN_PARKS'].values.reshape(-1,1))
scaler = MinMaxScaler()
blocks['UNHEALTHY_RESTAURANTS_STANDARD'] = scaler.fit_transform(blocks['UNHEALTHY_RESTAURANTS'].values.reshape(-1,1))

clustering_data = blocks[['PERC_TRADITIONAL_MEDICINE','PERC_ATENTION',
                   'PERC_NO_HEALTH_CONDITIONS','DRINKING_PLACES_STANDARD',
                   'PARKS_STANDARD','UNHEALTHY_RESTAURANTS_STANDARD']]

clustering_data.dropna(inplace=True)
kmeans = KMeans(n_clusters=5, random_state=0)
kmeans.fit(clustering_data)
clustering_data['VULNERABILITY_LEVEL'] = kmeans.labels_ + 1
grouped_table = clustering_data.groupby('VULNERABILITY_LEVEL').agg('mean')
clustering_data.replace({'VULNERABILITY_LEVEL': {1:3, 2:4, 3:1, 4:5, 5:2}}, inplace=True)
blocks['VULNERABILITY_LEVEL'] = 0
blocks.iloc[list(clustering_data.index),-1] = clustering_data.VULNERABILITY_LEVEL



kmeans = KMeans(n_clusters=4, random_state=0)
kmeans.fit(blocks.PERC_TRADITIONAL_MEDICINE[~blocks.PERC_TRADITIONAL_MEDICINE.isna()].values.reshape(-1,1))
blocks['TRADITIONAL_MEDICINE_CLUSTER'] = 0
blocks.loc[~blocks.PERC_TRADITIONAL_MEDICINE.isna(), 'TRADITIONAL_MEDICINE_CLUSTER'] = kmeans.labels_ + 1
blocks.PERC_TRADITIONAL_MEDICINE.fillna(0, inplace=True)
n_clust = len(blocks.TRADITIONAL_MEDICINE_CLUSTER.unique())
idx = np.argsort([blocks['PERC_TRADITIONAL_MEDICINE'][blocks['TRADITIONAL_MEDICINE_CLUSTER']==i].mean() for i in np.unique(blocks['TRADITIONAL_MEDICINE_CLUSTER'])])
lut = np.zeros_like(idx)
lut[idx] = np.arange(1,n_clust + 1,1)
blocks['TRADITIONAL_MEDICINE_CLUSTER'] = lut[blocks.TRADITIONAL_MEDICINE_CLUSTER]
blocks['TRADITIONAL_MEDICINE_CLUSTER'] = blocks['TRADITIONAL_MEDICINE_CLUSTER'] - 1
blocks.TRADITIONAL_MEDICINE_CLUSTER.value_counts()

kmeans = KMeans(n_clusters=4, random_state=0)
kmeans.fit(blocks.PERC_NO_HEALTH_CONDITIONS[~blocks.PERC_NO_HEALTH_CONDITIONS.isna()].values.reshape(-1,1))
blocks['HEALTH_PHYSICAL_CLUSTER'] = 0
blocks.loc[~blocks.PERC_NO_HEALTH_CONDITIONS.isna(), 'HEALTH_PHYSICAL_CLUSTER'] = kmeans.labels_ + 1
blocks.PERC_NO_HEALTH_CONDITIONS.fillna(0, inplace=True)
n_clust = len(blocks.HEALTH_PHYSICAL_CLUSTER.unique())
idx = np.argsort([blocks['PERC_NO_HEALTH_CONDITIONS'][blocks['HEALTH_PHYSICAL_CLUSTER']==i].mean() for i in np.unique(blocks['HEALTH_PHYSICAL_CLUSTER'])])
lut = np.zeros_like(idx)
lut[idx] = np.arange(1,n_clust + 1,1)
blocks['HEALTH_PHYSICAL_CLUSTER'] = lut[blocks.HEALTH_PHYSICAL_CLUSTER]
blocks['HEALTH_PHYSICAL_CLUSTER'] = blocks['HEALTH_PHYSICAL_CLUSTER'] - 1
blocks.HEALTH_PHYSICAL_CLUSTER.value_counts()


blocks_export = blocks[['geometry','ESTRATO','TRADITIONAL_MEDICINE_CLUSTER',
       'HEALTH_PHYSICAL_CLUSTER', 'VULNERABILITY_LEVEL']]


import geopandas as gpd
from shapely.wkt import loads
import re

simpledec = re.compile(r"\d*\.\d+")
def mround(match):
    return "{:.8f}".format(float(match.group()))

blocks_export.geometry = blocks_export.geometry.apply(lambda x: loads(re.sub(simpledec, mround, x.wkt)))

blocks_export.to_file("blocks.geojson", driver="GeoJSON")


urban_parks.to_file("urban_parks.geojson", driver="GeoJSON")

unhealthy_gpdf.to_file("unhealthy_food.geojson", driver="GeoJSON")
