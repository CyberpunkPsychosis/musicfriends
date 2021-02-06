package com.music.friends.app.utils;

import cn.hutool.core.util.IdUtil;
import cn.hutool.core.util.StrUtil;
import com.aliyun.oss.ClientException;
import com.aliyun.oss.OSS;
import com.aliyun.oss.OSSClientBuilder;
import com.aliyun.oss.OSSException;
import com.aliyun.oss.model.DeleteObjectsRequest;
import com.aliyun.oss.model.DeleteObjectsResult;
import com.aliyun.oss.model.PutObjectRequest;
import com.music.friends.app.exception.CustomException;
import com.music.friends.app.exception.ExceptionEnum;

import java.io.File;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;

/**
 * 阿里巴巴对象存储工具类
 */
public class AlibabaOSSUtil {

    private static final String HTTP = "http://";

    private static final String ENDPOINT = "oss-cn-beijing.aliyuncs.com";

    private static final String ACCESSKEY_ID = "LTAI4G3U4QzzHAvLi8UDDeJK";

    private static final String ACCESSKEY_SECRET = "YIlYsvbQNitCDB9a3mkfPNWhEAiTlV";

    private static final String BUCKET_NAME = "music-friends";

    private static final String SEPARATOR = "/";

    private static final String SPOT = ".";

    private static final String PREFIX = HTTP + BUCKET_NAME + SPOT + ENDPOINT + SEPARATOR;

    public static String fileUpload(String path, String account, String dirName) throws CustomException{
        try {
            String suffix = StrUtil.sub(path, path.lastIndexOf("."), path.length());
            String objectName = account + SEPARATOR + dirName + SEPARATOR + IdUtil.simpleUUID() + suffix;
            OSS ossClient = new OSSClientBuilder().build(ENDPOINT, ACCESSKEY_ID, ACCESSKEY_SECRET);
            PutObjectRequest putObjectRequest =
                    new PutObjectRequest(BUCKET_NAME, objectName,
                            new File(path));
            ossClient.putObject(putObjectRequest);
            ossClient.shutdown();
            return HTTP + BUCKET_NAME + SPOT + ENDPOINT + SEPARATOR + objectName;
        } catch (OSSException | ClientException e) {
            e.printStackTrace();
            throw new CustomException(ExceptionEnum.OSS_ERROR_EXCEPTION);
        }
    }

    public static String streamUpload(InputStream inputStream, String account, String dirName, String suffix) throws CustomException{
        try {
            String objectName = account + SEPARATOR + dirName + SEPARATOR + IdUtil.simpleUUID() + suffix;
            OSS ossClient = new OSSClientBuilder().build(ENDPOINT, ACCESSKEY_ID, ACCESSKEY_SECRET);
            ossClient.putObject(BUCKET_NAME, objectName, inputStream);
            ossClient.shutdown();
            return HTTP + BUCKET_NAME + SPOT + ENDPOINT + SEPARATOR + objectName;
        } catch (OSSException | ClientException e) {
            e.printStackTrace();
            throw new CustomException(ExceptionEnum.OSS_ERROR_EXCEPTION);
        }
    }

    public static void delete(String url) throws CustomException{
        String objectName = url.substring(PREFIX.length());
        try {
            OSS ossClient = new OSSClientBuilder().build(ENDPOINT, ACCESSKEY_ID, ACCESSKEY_SECRET);
            ossClient.deleteObject(BUCKET_NAME, objectName);
            ossClient.shutdown();
        } catch (OSSException | ClientException e) {
            e.printStackTrace();
            throw new CustomException(ExceptionEnum.OSS_ERROR_EXCEPTION);
        }
    }

    /**
     * flag false返回删除成功的文件列表，true返回删除失败的文件列表
     */
    public static List<String> batchDelete(List<String> urls, boolean flag) throws CustomException{
        try {
            List<String> objectNames = new ArrayList<>();
            urls.forEach(x -> {
                objectNames.add(x.substring(PREFIX.length()));
            });
            OSS ossClient = new OSSClientBuilder().build(ENDPOINT, ACCESSKEY_ID, ACCESSKEY_SECRET);
            DeleteObjectsResult deleteObjectsResult = ossClient
                    .deleteObjects(new DeleteObjectsRequest(BUCKET_NAME).withKeys(objectNames).withQuiet(flag));
            List<String> deletedObjects = deleteObjectsResult.getDeletedObjects();
            ossClient.shutdown();
            return deletedObjects;
        } catch (OSSException | ClientException e) {
            e.printStackTrace();
            throw new CustomException(ExceptionEnum.OSS_ERROR_EXCEPTION);
        }
    }
}
