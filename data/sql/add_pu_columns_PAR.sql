alter table PAR add column PU_ID bigint;
update PAR set PU_ID = ID;
update PAR set ID = NULL;

alter table PAR add column PU_KMENOVE_CISLO_PAR integer;
update PAR set PU_KMENOVE_CISLO_PAR = KMENOVE_CISLO_PAR;

alter table PAR add column PU_PODDELENI_CISLA_PAR integer;
update PAR set PU_PODDELENI_CISLA_PAR = PODDELENI_CISLA_PAR;

alter table PAR add column PU_VYMERA_PARCELY integer;

alter table PAR add column PU_VYMERA_PARCELY_ABS_ROZDIL integer;

alter table PAR add column PU_VYMERA_PARCELY_MEZNI_ODCHYLKA integer;

alter table PAR add column PU_VYMERA_PARCELY_MAX_KODCHB_KOD integer;

alter table PAR add column PU_KATEGORIE integer;

alter table PAR add column PU_VZDALENOST integer;

alter table PAR add column PU_CENA real;

alter table PAR add column PU_BPEJ_BPEJCENA_VYMERA_CENA text;

commit