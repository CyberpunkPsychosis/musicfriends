package com.music.friends.app.exception;

public enum ExceptionEnum {

    DATA_NULL_EXCEPTION("A-001", "数据为空"),
    PARAM_NULL_EXCEPTION("A-002", "参数为空"),
    OSS_ERROR_EXCEPTION("B-001", "OSS操作失败");

    ExceptionEnum(String code, String message) {
        this.code = code;
        this.message = message;
    }

    public final String code;

    public final String message;

    public String getCode() {
        return code;
    }

    public String getMessage() {
        return message;
    }
}
