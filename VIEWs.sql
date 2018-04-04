--	VIEWs 25.04.2016

DROP	VIEW vcontracts;
DROP	VIEW vpersons;
DROP	VIEW valarms;
DROP	VIEW vbids;
DROP	VIEW vmail_to;
DROP	VIEW vorganizations;

CREATE	VIEW vorganizations AS SELECT o.*, r.rname FROM organizations o, region r WHERE id=region;
CREATE	VIEW vcontracts AS SELECT c.*, o.label, o.bname, o.fname, o.region, o.rname FROM vorganizations o, contracts c WHERE c.id_org = o.id_org;

--	INSERT INTO contracts (id_contr, id_org) values (0,0)
--	INSERT INTO organizations (id_org) values (0);
--	insert	into transports (id_ts) values (0);
--	insert	into organizations (id_org) values (0);
--	insert	into atts (id_att) values (0);
--	insert	INTO persons (id_persn) values (0);

--CREATE	VIEW vtransports AS SELECT t.*, o.bname AS oname, y.ttname FROM transports t, organizations o, ts_types y  WHERE t.id_org = o.id_org AND t.ts_type = y.id_tts;
DROP	VIEW vtransports;
CREATE  VIEW vtransports AS SELECT t.*, o.bname AS oname, y.ttname, r.rname FROM transports t, organizations o, ts_types y, region r WHERE t.id_org = o.id_org AND t.ts_type = y.id_tts AND r.id = t.region;

DROP	VIEW voatts;
CREATE	VIEW voatts AS SELECT a.*, t.gosnum, o.id_org, o.label AS olabel, o.bname AS obname, o.region, t.bm_ssys FROM atts a, transports t, organizations o WHERE a.autos = t.id_ts AND t.id_org = o.id_org;

--	Прописать подсистемы для Организаций на основании данных по машинам
--	UPDATE	organizations SET bm_ssys = 2 WHERE id_org IN (SELECT id_org FROM transports WHERE id_org > 0 AND bm_ssys = 2);
--	UPDATE	organizations SET bm_ssys = 4 WHERE id_org IN (SELECT id_org FROM transports WHERE id_org > 0 AND bm_ssys = 4);
--	UPDATE	organizations SET bm_ssys = 8 WHERE id_org IN (SELECT id_org FROM transports WHERE id_org > 0 AND bm_ssys = 8);
--	UPDATE	organizations SET bm_ssys = 16 WHERE id_org IN (SELECT id_org FROM transports WHERE id_org > 0 AND bm_ssys = 16);
--	UPDATE	organizations SET bm_ssys = 32 WHERE id_org IN (SELECT id_org FROM transports WHERE id_org > 0 AND bm_ssys = 32);
--	UPDATE	organizations SET bm_ssys = 128 WHERE id_org IN (SELECT id_org FROM transports WHERE id_org > 0 AND bm_ssys = 128);

	UPDATE	transports SET region = 0 WHERE region IS NULL;
	UPDATE	transports SET id_org =0 WHERE id_org IS NULL;
	UPDATE	transports SET ts_type =0 WHERE ts_type IS NULL;

--	20.05.2016
CREATE	VIEW vpersons AS SELECT p.*, o.id_org, o.bname AS obname, o.region, o.rname FROM persons p,  person2x x, vorganizations o WHERE p.id_persn = x.id_persn AND x.id_org = o.id_org;
--	26.05.2016
CREATE UNIQUE INDEX idx_unique_organizations ON organizations USING btree (inn);
--	22.06.2016
CREATE	VIEW vbids AS SELECT b.*, t.bname, o.bname AS obname, o.region, o.rname FROM bids b, bid_type t, vorganizations o WHERE b.bm_btype=t.code  AND b.id_org = o.id_org;
--	01.07.2016
UPDATE bid_stat SET bm_btype = bm_btype | 2048 WHERE code IN (128, 1024, 2048);
UPDATE bid_stat SET bm_btype = bm_btype | 32 WHERE code IN (128, 1024, 2048);
--	04.07.2016
CREATE  VIEW valarms AS SELECT a.*, t.bname, o.bname AS obname FROM alarms a, bid_type t, vorganizations o WHERE a.bm_btype=t.code AND a.id_org = o.id_org;
--	05.07.2016
--	UPDATE alarms SET bm_bstat = bm_btype WHERE message LIKE 'type:%';
--	UPDATE alarms SET bm_btype=128 WHERE message LIKE 'type: "Переименование организации%';
--	UPDATE alarms SET bm_btype=32 WHERE message LIKE 'type: "Временное отключении ТС %';
--	UPDATE alarms SET bm_btype=256 WHERE message LIKE 'type: "Письмо-оповещение о переносе БО%';
--	UPDATE alarms SET bm_btype=64 WHERE message LIKE 'type: "Передача ТС в другую организацию%';
--	UPDATE alarms SET bm_btype=4096 WHERE message LIKE 'type: "Претензии, проблемы и прочее%';

-- 2016-10-11	atts & transports +	transport_id	device_id
-- ../sql/alter_contrdb-20160819.sql

DROP VIEW vhistory;	-- 06.04.2017
CREATE VIEW vhistory AS SELECT h.*, c.cnum FROM history h LEFT JOIN contracts c ON c.id_contr = h.id_contr;

-- 2017-05-15	mail_to.sql 
CREATE VIEW vmail_to AS SELECT m.*, o.bname AS obname, o.region, o.rname FROM mail_to m, vorganizations o WHERE m.id_org = o.id_org;

-- 2017-07-11
-- 2018-01-31	DISTINCT
DROP	VIEW wtransports;
CREATE  VIEW wtransports AS SELECT DISTINCT t.*, o.bname AS oname, y.ttname, r.rname, a.mark AS amark, a.last_date, a.modele AS amodele, a.bm_wtime, b.bm_btype, b.bid_num AS bid, b.tm_creat, b.tm_close, b.id_bid
FROM transports t
	LEFT JOIN organizations o ON t.id_org = o.id_org
	LEFT JOIN ts_types y ON t.ts_type = y.id_tts
	LEFT JOIN region r ON r.id = t.region
	LEFT JOIN atts a ON t.device_id = a.device_id
	LEFT JOIN bids b ON b.id_org = o.id_org  AND (b.bm_btype & 8192) > 0 AND (b.bm_bstat & 69632) != 69632	-- and b.tm_close IS NULL
WHERE (bm_status & 15) > 0;

-- 2018-02-13
CREATE  VIEW wtransports AS SELECT t.*, o.bname AS oname, y.ttname, r.rname, a.mark AS amark, a.last_date, a.modele AS amodele, a.bm_wtime, b.bm_btype, b.bid_num AS bid, b.tm_creat, b.tm_close, b.id_bid
FROM transports t
	INNER JOIN organizations o ON t.id_org = o.id_org
	INNER JOIN ts_types y ON t.ts_type = y.id_tts
	INNER JOIN atts a ON t.id_ts = a.autos AND t.device_id = a.device_id
	LEFT JOIN region r ON r.id = t.region
	LEFT JOIN bids b ON b.id_org = o.id_org AND (b.id_bid IN (SELECT max(bids.id_bid) FROM bids WHERE bm_btype = 8192 AND bm_bstat & 69632 != 69632 AND bids.id_org = t.id_org))
WHERE (bm_status & 15) > 0;

DROP	VIEW varms;
CREATE	VIEW varms AS SELECT a.*, o.bname AS oname, c.cnum, b.bid_num, o.region, o.rname
FROM arms a
	LEFT JOIN vorganizations o ON a.id_org = o.id_org
	LEFT JOIN contracts c ON a.id_contr = c.id_contr
	LEFT JOIN bids b ON a.id_bid = b.id_bid
	;
