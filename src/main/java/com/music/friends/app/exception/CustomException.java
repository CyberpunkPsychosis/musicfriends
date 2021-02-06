package com.music.friends.app.exception;


import cn.hutool.core.util.StrUtil;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.lang.reflect.Member;

public class CustomException extends RuntimeException{

    private static final Logger logger = LoggerFactory.getLogger(CustomException.class);

    private ExceptionEnum exceptionEnum;

    private String code;

    private String message;

    public CustomException() {
        super();
    }

    public CustomException(String code, String message) {
        super(message);
        this.code = code;
        this.message = message;
    }

    public CustomException(String message){
        super(message);
        this.message = message;
    }

    public CustomException(ExceptionEnum exceptionEnum){
        super(exceptionEnum.message);
        this.exceptionEnum = exceptionEnum;
    }

    public CustomException(String code, String message, Throwable cause) {
        super(message,cause);
        this.code = code;
        this.message = message;
    }

    public CustomException(ExceptionEnum exceptionEnum, Throwable cause){
        super(exceptionEnum.message, cause);
        this.exceptionEnum = exceptionEnum;
    }

    public ExceptionEnum getExceptionEnum() {
        return exceptionEnum;
    }

    public void setExceptionEnum(ExceptionEnum exceptionEnum) {
        this.exceptionEnum = exceptionEnum;
    }

    public String getCode() {
        return code;
    }

    public void setCode(String code) {
        this.code = code;
    }

    @Override
    public String getMessage() {
        if (StrUtil.hasBlank(this.message)){
            return this.exceptionEnum.getMessage();
        }
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    @Override
    public void printStackTrace() {
        super.printStackTrace();
        if (exceptionEnum != null){
            logger.info("异常代码: " + exceptionEnum.code + "  异常信息: " + exceptionEnum.message);
            return;
        }
        logger.info("异常代码: " + code + "异常信息: " + message);
    }
}
