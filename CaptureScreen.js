import React, { useState, useEffect, useRef } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Alert, Image } from 'react-native';
import { Camera } from 'expo-camera';
import * as ImagePicker from 'expo-image-picker';

export default function CaptureScreen() {
  const [hasPermission, setHasPermission] = useState(null);
  const [type, setType] = useState(Camera.Constants.Type.back);
  const [capturedImage, setCapturedImage] = useState(null);
  const cameraRef = useRef(null);

  useEffect(() => {
    (async () => {
      const { status } = await Camera.requestCameraPermissionsAsync();
      setHasPermission(status === 'granted');
      
      if (status !== 'granted') {
        Alert.alert(
          '카메라 권한 필요',
          '약 봉투를 촬영하기 위해 카메라 권한이 필요합니다.',
          [
            {
              text: '설정으로 이동',
              onPress: () => {
                // 권한 설정 페이지로 이동하는 로직 (플랫폼별로 다름)
                Alert.alert('설정', '앱 설정에서 카메라 권한을 허용해주세요.');
              }
            },
            {
              text: '취소',
              style: 'cancel'
            }
          ]
        );
      }
    })();
  }, []);

  const takePicture = async () => {
    if (cameraRef.current) {
      try {
        const photo = await cameraRef.current.takePictureAsync({
          quality: 0.8,
          base64: false,
        });
        
        // 촬영된 이미지 URI를 상태로 저장
        setCapturedImage(photo.uri);
        
        // 이미지 URI를 콘솔에 출력 (추후 업로드/처리용)
        console.log('Captured Image URI:', photo.uri);
        
        // 촬영 성공 알림
        Alert.alert(
          '촬영 완료',
          '사진이 촬영되었습니다.',
          [
            {
              text: '다시 촬영',
              onPress: () => setCapturedImage(null)
            },
            {
              text: '확인',
              style: 'default'
            }
          ]
        );
      } catch (error) {
        console.error('Error taking picture:', error);
        Alert.alert('오류', '사진 촬영 중 오류가 발생했습니다.');
      }
    }
  };

  if (hasPermission === null) {
    return (
      <View style={styles.container}>
        <Text style={styles.message}>카메라 권한 확인 중...</Text>
      </View>
    );
  }

  if (hasPermission === false) {
    return (
      <View style={styles.container}>
        <Text style={styles.message}>카메라 권한이 거부되었습니다.</Text>
        <Text style={styles.subMessage}>앱 설정에서 카메라 권한을 허용해주세요.</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerTop}>
          <TouchableOpacity style={styles.backButton}>
            <Text style={styles.arrow}>←</Text>
            <Text style={styles.backText}>뒤로가기</Text>
          </TouchableOpacity>
          <View style={styles.appTitle}>
            <Text style={styles.appTitleText}>
              <Text style={styles.appTitleMed}>약</Text>
              <Text style={styles.appTitleRest}>을먹자</Text>
            </Text>
            <Text style={styles.pillIcons}>💊💊</Text>
          </View>
        </View>
        <Text style={styles.mainTitle}>검색</Text>
      </View>

      {/* Main Content */}
      <View style={styles.mainContent}>
        <Text style={styles.instructionText}>약 봉투를 네모 안에 맞춰주세요.</Text>
        
        {/* Camera View */}
        <View style={styles.cameraContainer}>
          {capturedImage ? (
            <Image source={{ uri: capturedImage }} style={styles.capturedImage} />
          ) : (
            <Camera
              ref={cameraRef}
              style={styles.camera}
              type={type}
              ratio="16:9"
            />
          )}
        </View>
      </View>

      {/* Capture Button */}
      <TouchableOpacity
        style={styles.captureButton}
        onPress={takePicture}
        disabled={!!capturedImage}
      >
        <View style={styles.captureIcon}>
          <View style={styles.iconSquare} />
          <View style={[styles.cornerBracket, { top: 0, left: 0 }]} />
          <View style={[styles.cornerBracket, { top: 0, right: 0, transform: [{ rotate: '90deg' }] }]} />
          <View style={[styles.cornerBracket, { bottom: 0, right: 0, transform: [{ rotate: '180deg' }] }]} />
          <View style={[styles.cornerBracket, { bottom: 0, left: 0, transform: [{ rotate: '270deg' }] }]} />
        </View>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    width: 390,
    height: 844,
    alignSelf: 'center',
  },
  message: {
    flex: 1,
    textAlign: 'center',
    marginTop: 200,
    fontSize: 18,
    color: '#333',
  },
  subMessage: {
    textAlign: 'center',
    fontSize: 14,
    color: '#666',
    marginTop: 10,
  },
  header: {
    backgroundColor: '#c2cdff',
    paddingTop: 20,
    paddingBottom: 30,
    paddingHorizontal: 20,
  },
  headerTop: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  backButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 5,
  },
  arrow: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#5271ff',
  },
  backText: {
    fontSize: 20,
    fontWeight: '500',
    color: '#5271ff',
  },
  appTitle: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  appTitleText: {
    fontSize: 20,
    fontWeight: '500',
  },
  appTitleMed: {
    color: '#5271ff',
  },
  appTitleRest: {
    color: '#000000',
  },
  pillIcons: {
    fontSize: 18,
  },
  mainTitle: {
    textAlign: 'center',
    fontSize: 42,
    fontWeight: 'bold',
    color: '#2c2c2c',
  },
  mainContent: {
    flex: 1,
    backgroundColor: '#fff',
    paddingTop: 20,
    paddingHorizontal: 20,
    paddingBottom: 100,
  },
  instructionText: {
    textAlign: 'center',
    fontSize: 18,
    fontWeight: '500',
    color: '#2c2c2c',
    marginBottom: 15,
  },
  cameraContainer: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    borderRadius: 12,
    overflow: 'hidden',
    position: 'relative',
  },
  camera: {
    flex: 1,
  },
  capturedImage: {
    flex: 1,
    width: '100%',
    resizeMode: 'contain',
  },
  captureButton: {
    position: 'absolute',
    bottom: 30,
    alignSelf: 'center',
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: '#5170ff',
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#5170ff',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.4,
    shadowRadius: 6,
    elevation: 8,
    zIndex: 1000,
  },
  captureIcon: {
    width: 60,
    height: 60,
    alignItems: 'center',
    justifyContent: 'center',
    position: 'relative',
  },
  iconSquare: {
    width: 42,
    height: 42,
    borderWidth: 2,
    borderColor: '#fff',
  },
  cornerBracket: {
    position: 'absolute',
    width: 12,
    height: 12,
    borderColor: '#fff',
    borderWidth: 2,
    borderRightWidth: 0,
    borderBottomWidth: 0,
  },
});

