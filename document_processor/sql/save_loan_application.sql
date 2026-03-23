CREATE OR REPLACE FUNCTION sp_save_loan_application(
    p_payload JSONB,
    p_user_id INT,
    p_application_id INT DEFAULT NULL
)
RETURNS INT AS $$
DECLARE
    v_client_id INT;
    v_app_id INT;
    v_personal JSONB;
    v_loan JSONB;
    v_financial JSONB;
    v_collateral JSONB;
    v_contacts JSONB;
    v_collateral_owner_id INT;
    v_collateral_owner_type TEXT;
    v_selected_types TEXT[];
    v_type TEXT;
    v_base_col_id INT;
BEGIN
    v_personal := p_payload->'personal';
    v_loan := p_payload->'loan';
    v_financial := p_payload->'financial';
    v_collateral := p_payload->'collateral';
    v_contacts := p_payload->'contacts';

    -- 1. Handle Client (Borrower)
    -- Upsert logic
    SELECT id INTO v_client_id 
    FROM document_processor_client 
    WHERE pasport_seriya = (v_personal->>'pasport_seriya') 
       OR jshshir = (v_personal->>'jshshir')::BIGINT
    LIMIT 1;

    IF v_client_id IS NOT NULL THEN
        UPDATE document_processor_client SET
            fish = UPPER(COALESCE(v_personal->>'fish', fish)),
            fish_inisiali = UPPER(COALESCE(v_personal->>'fish_inisiali', fish_inisiali)),
            pasport_berilgan = COALESCE(v_personal->>'pasport_berilgan', pasport_berilgan),
            tugilgan_sana = COALESCE((v_personal->>'tugilgan_sana')::DATE, tugilgan_sana),
            jinsi = COALESCE(v_personal->>'jinsi', jinsi),
            telefon = COALESCE(v_personal->>'telefon', telefon),
            manzil = COALESCE(v_personal->>'manzil', manzil),
            updated_at = NOW()
        WHERE id = v_client_id;
    ELSE
        INSERT INTO document_processor_client (
            fish, fish_inisiali, pasport_seriya, pasport_berilgan, jshshir, 
            tugilgan_sana, jinsi, telefon, manzil, created_at, updated_at
        ) VALUES (
            UPPER(v_personal->>'fish'), UPPER(v_personal->>'fish_inisiali'), 
            v_personal->>'pasport_seriya', v_personal->>'pasport_berilgan', 
            (v_personal->>'jshshir')::BIGINT, (v_personal->>'tugilgan_sana')::DATE, 
            v_personal->>'jinsi', v_personal->>'telefon', v_personal->>'manzil', NOW(), NOW()
        ) RETURNING id INTO v_client_id;
    END IF;

    -- 2. Handle Loan Application
    IF p_application_id IS NOT NULL THEN
        UPDATE document_processor_loanapplication SET
            client_id = v_client_id,
            payload = p_payload,
            updated_at = NOW()
        WHERE id = p_application_id;
        v_app_id := p_application_id;
    ELSE
        INSERT INTO document_processor_loanapplication (
            client_id, status, is_deleted, created_by_id, payload, created_at, updated_at
        ) VALUES (
            v_client_id, 'pending_moderator', FALSE, p_user_id, p_payload, NOW(), NOW()
        ) RETURNING id INTO v_app_id;
    END IF;

    -- 3. Handle Loan Details
    INSERT INTO document_processor_loandetails (
        application_id, shartnoma_raqami, shartnoma_sanasi, boshlanish_sanasi, tugash_sanasi,
        miqdori, miqdori_soz, muddat_oy, muddat_oy_soz, foiz, foiz_soz, turi, grafik_turi, grafik_matni
    ) VALUES (
        v_app_id, v_loan->>'shartnoma_raqami', (v_loan->>'shartnoma_sanasi')::DATE, 
        (v_loan->>'boshlanish_sanasi')::DATE, (v_loan->>'tugash_sanasi')::DATE,
        (v_loan->>'miqdori')::BIGINT, v_loan->>'miqdori_soz', v_loan->>'muddat_oy', 
        v_loan->>'muddat_oy_soz', v_loan->>'foiz', v_loan->>'foiz_soz', 
        COALESCE(v_loan->>'turi', 'mikroqarz'), COALESCE(v_loan->>'grafik_turi', 'differensial'), 
        v_loan->>'grafik_matni'
    )
    ON CONFLICT (application_id) DO UPDATE SET
        shartnoma_raqami = EXCLUDED.shartnoma_raqami,
        shartnoma_sanasi = EXCLUDED.shartnoma_sanasi,
        boshlanish_sanasi = EXCLUDED.boshlanish_sanasi,
        tugash_sanasi = EXCLUDED.tugash_sanasi,
        miqdori = EXCLUDED.miqdori,
        miqdori_soz = EXCLUDED.miqdori_soz,
        muddat_oy = EXCLUDED.muddat_oy,
        muddat_oy_soz = EXCLUDED.muddat_oy_soz,
        foiz = EXCLUDED.foiz,
        foiz_soz = EXCLUDED.foiz_soz,
        turi = EXCLUDED.turi,
        grafik_turi = EXCLUDED.grafik_turi,
        grafik_matni = EXCLUDED.grafik_matni;

    -- 4. Handle Contacts
    DELETE FROM document_processor_contactperson WHERE application_id = v_app_id;
    INSERT INTO document_processor_contactperson (application_id, fish, telefon, qarindoshlik)
    SELECT v_app_id, c->>'fish', c->>'telefon', c->>'qarindoshlik'
    FROM jsonb_array_elements(v_contacts) AS c;

    -- 5. Handle Financial Info
    INSERT INTO document_processor_financialinfo (
        application_id, aloqa_uy_tel, aloqa_uyali_tel, aloqa_ish_tel,
        ish_muassasa, ish_manzil, ish_lavozim,
        daromad_asosiy, daromad_orindosh, daromad_boshqa, daromad,
        xarajat_kommunal, xarajat_oilaviy, xarajat_boshqa, xarajatlar,
        majburiyatlar, filial_nomi, filial_boshligi, 
        filial_boshligi_inisiali, tashkilot_nomi, direktor_fish, direktor_fish_inisiali
    ) VALUES (
        v_app_id, v_financial->>'aloqa_uy_tel', v_financial->>'aloqa_uyali_tel', v_financial->>'aloqa_ish_tel',
        v_financial->>'ish_muassasa', v_financial->>'ish_manzil', v_financial->>'ish_lavozim',
        (v_financial->>'daromad_asosiy')::BIGINT, (v_financial->>'daromad_orindosh')::BIGINT, (v_financial->>'daromad_boshqa')::BIGINT, (v_financial->>'daromad')::BIGINT,
        (v_financial->>'xarajat_kommunal')::BIGINT, (v_financial->>'xarajat_oilaviy')::BIGINT, (v_financial->>'xarajat_boshqa')::BIGINT, (v_financial->>'xarajatlar')::BIGINT,
        v_financial->>'majburiyatlar', 
        COALESCE(v_financial->>'filial_nomi', 'Buxoro filiali'), 
        UPPER(v_financial->>'filial_boshligi'), UPPER(v_financial->>'filial_boshligi_inisiali'),
        v_financial->>'tashkilot_nomi', UPPER(v_financial->>'direktor_fish'), UPPER(v_financial->>'direktor_fish_inisiali')
    )
    ON CONFLICT (application_id) DO UPDATE SET
        aloqa_uy_tel = EXCLUDED.aloqa_uy_tel, aloqa_uyali_tel = EXCLUDED.aloqa_uyali_tel, aloqa_ish_tel = EXCLUDED.aloqa_ish_tel,
        ish_muassasa = EXCLUDED.ish_muassasa, ish_manzil = EXCLUDED.ish_manzil, ish_lavozim = EXCLUDED.ish_lavozim,
        daromad_asosiy = EXCLUDED.daromad_asosiy, daromad_orindosh = EXCLUDED.daromad_orindosh, daromad_boshqa = EXCLUDED.daromad_boshqa, daromad = EXCLUDED.daromad,
        xarajat_kommunal = EXCLUDED.xarajat_kommunal, xarajat_oilaviy = EXCLUDED.xarajat_oilaviy, xarajat_boshqa = EXCLUDED.xarajat_boshqa, xarajatlar = EXCLUDED.xarajatlar,
        majburiyatlar = EXCLUDED.majburiyatlar, filial_nomi = EXCLUDED.filial_nomi,
        filial_boshligi = EXCLUDED.filial_boshligi, filial_boshligi_inisiali = EXCLUDED.filial_boshligi_inisiali,
        tashkilot_nomi = EXCLUDED.tashkilot_nomi, direktor_fish = EXCLUDED.direktor_fish, direktor_fish_inisiali = EXCLUDED.direktor_fish_inisiali;

    -- 6. Handle Collaterals
    DELETE FROM document_processor_collateral WHERE application_id = v_app_id;

    v_collateral_owner_type := COALESCE(v_collateral->>'owner_type', 'borrower');
    
    IF v_collateral_owner_type = 'borrower' THEN
        v_collateral_owner_id := v_client_id;
    ELSE
        -- Find or create other client for collateral
        SELECT id INTO v_collateral_owner_id 
        FROM document_processor_client 
        WHERE pasport_seriya = (v_collateral->>'owner_passport') 
           OR jshshir = (v_collateral->>'owner_jshshir')::BIGINT
        LIMIT 1;

        IF v_collateral_owner_id IS NULL THEN
            INSERT INTO document_processor_client (
                fish, fish_inisiali, pasport_seriya, pasport_berilgan, jshshir, 
                tugilgan_sana, manzil, jinsi, created_at, updated_at
            ) VALUES (
                UPPER(v_collateral->>'owner_fish'), UPPER(v_collateral->>'owner_initials'),
                v_collateral->>'owner_passport', v_collateral->>'owner_passport_given_by',
                (v_collateral->>'owner_jshshir')::BIGINT, (v_collateral->>'owner_birth_date')::DATE,
                v_collateral->>'owner_address', v_collateral->>'owner_gender', NOW(), NOW()
            ) RETURNING id INTO v_collateral_owner_id;
        END IF;
    END IF;

    -- Process selected types
    v_selected_types := ARRAY(SELECT jsonb_array_elements_text(v_collateral->'selected_types'));
    
    FOREACH v_type IN ARRAY v_selected_types LOOP
        IF v_type = 'kochmas_mulk' THEN v_type := 'kochmas'; END IF;

        INSERT INTO document_processor_collateral (
            application_id, type, owner_type, owner_client_id,
            notarius_fish, notarius_address, reestr_number, reestr_date
        ) VALUES (
            v_app_id, v_type, v_collateral_owner_type, v_collateral_owner_id,
            v_collateral->>'notarius_fish', v_collateral->>'notarius_address',
            v_collateral->>'reestr_number', (v_collateral->>'reestr_date')::DATE
        ) RETURNING id INTO v_base_col_id;

        IF v_type = 'avto' THEN
            INSERT INTO document_processor_autocollateral (
                collateral_id, nomi, kuzov_turi, kuzov_raqami, dvigatel, shassi, 
                rang, yil, texpasport, texpasport_sana, manzil, davlat_raqami, bahosi, bahosi_soz
            ) VALUES (
                v_base_col_id, UPPER(v_collateral->>'avto_nomi'), v_collateral->>'avto_kuzov_turi',
                v_collateral->>'avto_kuzov', v_collateral->>'avto_dvigatel', 
                COALESCE(v_collateral->>'avto_shassi', 'RAKAMSIZ'), v_collateral->>'avto_rang',
                (v_collateral->>'avto_yil')::INT, v_collateral->>'avto_texpasport',
                (v_collateral->>'avto_texpasport_sana')::DATE, v_collateral->>'avto_manzil',
                UPPER(v_collateral->>'avto_raqam'), (v_collateral->>'avto_bahosi')::BIGINT, v_collateral->>'avto_bahosi_soz'
            );
        ELSIF v_type = 'kochmas' THEN
            INSERT INTO document_processor_realestatecollateral (
                collateral_id, turi, umumiy_maydon, qurilish_maydon, foydalanish_maydon,
                yashash_maydon, reestr_raqami, kadastr_raqami, manzil, bahosi, bahosi_soz
            ) VALUES (
                v_base_col_id, v_collateral->>'mulk_turi', v_collateral->>'mulk_umumiy_yer_maydoni',
                v_collateral->>'mulk_qurilish_osti_maydoni', v_collateral->>'mulk_umumiy_foydalanish_maydoni',
                v_collateral->>'mulk_yashash_maydoni', v_collateral->>'mulk_reestr_raqami',
                v_collateral->>'mulk_kadastr_raqami', v_collateral->>'mulk_manzili',
                (v_collateral->>'mulk_bahosi')::BIGINT, v_collateral->>'mulk_bahosi_soz'
            );
        ELSIF v_type = 'tilla' THEN
            INSERT INTO document_processor_goldcollateral (
                collateral_id, nomi, probi, vazni, soni, bahosi, bahosi_soz
            ) VALUES (
                v_base_col_id, v_collateral->>'tilla_nomi', v_collateral->>'tilla_probi',
                v_collateral->>'tilla_vazni', (v_collateral->>'tilla_soni')::INT,
                (v_collateral->>'tilla_bahosi')::BIGINT, v_collateral->>'tilla_bahosi_soz'
            );
        ELSIF v_type = 'sugurta' THEN
            INSERT INTO document_processor_insurancecollateral (
                collateral_id, kompaniya, polis_raqami, sana, summa, summa_soz
            ) VALUES (
                v_base_col_id, v_collateral->>'sugurta_kompaniya', v_collateral->>'sugurta_polisi',
                (v_collateral->>'sugurta_sana')::DATE, (v_collateral->>'sugurta_summa')::BIGINT,
                v_collateral->>'sugurta_summa_soz'
            );
        END IF;
    END LOOP;

    RETURN v_app_id;
END;
$$ LANGUAGE plpgsql;
