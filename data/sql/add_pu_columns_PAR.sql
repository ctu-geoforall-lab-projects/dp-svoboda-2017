alter table PAR add column PU_KMENOVE_CISLO_PAR integer;
update PAR set PU_KMENOVE_CISLO_PAR = KMENOVE_CISLO_PAR;

alter table PAR add column PU_PODDELENI_CISLA_PAR integer;
update PAR set PU_PODDELENI_CISLA_PAR = PODDELENI_CISLA_PAR;

alter table PAR add column PU_VYMERA_PARCELY integer;
update PAR set PU_VYMERA_PARCELY = VYMERA_PARCELY;

alter table PAR add column PU_KATEGORIE integer default 1;
