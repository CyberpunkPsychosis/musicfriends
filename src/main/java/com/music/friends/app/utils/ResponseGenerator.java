package com.music.friends.app.utils;

import cn.hutool.http.HttpStatus;

public class ResponseGenerator {
    private static final String DEFAULT_SUCCESS_MESSAGE = "SUCCESS";
    private static final String DEFAULT_FAIL_MESSAGE = "FAIL";

    public static ResponseResult getSuccessResult() {
        return new ResponseResult()
                .setCode(HttpStatus.HTTP_OK)
                .setMessage(DEFAULT_SUCCESS_MESSAGE);
    }

    public static ResponseResult getSuccessResult(String key, Object data) {
        return new ResponseResult()
                .setCode(HttpStatus.HTTP_OK)
                .setMessage(DEFAULT_SUCCESS_MESSAGE)
                .setData(key, data);
    }

    public static ResponseResult getFailResult(String message) {
        return new ResponseResult()
                .setCode(HttpStatus.HTTP_BAD_REQUEST)
                .setMessage(message);
    }

    public static ResponseResult getFailResult(){
        return new ResponseResult()
                .setCode(HttpStatus.HTTP_BAD_REQUEST)
                .setMessage(DEFAULT_FAIL_MESSAGE);
    }
}
