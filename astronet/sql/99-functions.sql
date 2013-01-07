DROP FUNCTION IF EXISTS delete_comment(varchar, bigint);
CREATE FUNCTION delete_comment(varchar, bigint) RETURNS integer AS $$
DECLARE
    auth integer;
BEGIN
    auth := (SELECT check_auth($1, $2));
    IF auth <> 1 THEN
        RETURN auth;
    END IF;

    DELETE FROM comments WHERE string_id=$1;
    RETURN 1;
END;
$$ LANGUAGE 'plpgsql';

DROP FUNCTION IF EXISTS update_comment(varchar, bigint, varchar);
CREATE FUNCTION update_comment(varchar, bigint, varchar) RETURNS integer AS $$
DECLARE
    auth integer;
BEGIN
    auth := (SELECT check_auth($1, $2));
    IF auth <> 1 THEN
        RETURN auth;
    END IF;

    UPDATE comments SET body=$3 WHERE string_id=$1;
    RETURN 1;
END;
$$ LANGUAGE 'plpgsql';

DROP FUNCTION IF EXISTS check_auth(varchar, bigint);
CREATE FUNCTION check_auth(varchar, bigint) RETURNS integer AS $$
BEGIN
    IF (SELECT COUNT(*) FROM comments WHERE string_id=$1) = 0 THEN
        RETURN -1;
    END IF;
    IF (SELECT COUNT(*) FROM comments WHERE string_id=$1 AND
        author=$2) = 0 THEN
        RETURN -2;
    END IF;
    RETURN 1;
END;
$$ LANGUAGE 'plpgsql';

