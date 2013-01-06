DROP FUNCTION IF EXISTS delete_comment(varchar, bigint);
CREATE FUNCTION delete_comment(varchar, bigint) RETURNS integer AS $$
BEGIN
    IF (SELECT COUNT(*) FROM comments WHERE string_id=$1) = 0 THEN
        RETURN -1;
    END IF;
    IF (SELECT COUNT(*) FROM comments WHERE string_id=$1 AND
        author=$2) = 0 THEN
        RETURN -2;
    END IF;

    DELETE FROM comments WHERE string_id=$1;
    RETURN 1;
END;
$$ LANGUAGE 'plpgsql';
