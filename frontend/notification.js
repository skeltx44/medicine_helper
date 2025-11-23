// 알림 관리 스크립트
// 약 복용 알림을 관리하는 함수들

(function() {
    'use strict';

    // 알림 권한 요청
    async function requestNotificationPermission() {
        if (!('Notification' in window)) {
            console.log('이 브라우저는 알림을 지원하지 않습니다.');
            return false;
        }

        if (Notification.permission === 'granted') {
            return true;
        }

        if (Notification.permission !== 'denied') {
            const permission = await Notification.requestPermission();
            return permission === 'granted';
        }

        return false;
    }

    // 알림 표시
    function showNotification(title, body, options = {}) {
        if (Notification.permission === 'granted') {
            const notification = new Notification(title, {
                body: body,
                icon: options.icon || 'pill.png',
                badge: 'pill.png',
                tag: options.tag || 'medication-reminder',
                requireInteraction: options.requireInteraction || false,
                ...options
            });

            notification.onclick = function() {
                window.focus();
                notification.close();
            };

            return notification;
        }
    }

    // 약 복용 알림 스케줄 설정
    function scheduleMedicationNotifications() {
        const medications = JSON.parse(localStorage.getItem('medications') || '[]');
        
        if (medications.length === 0) {
            return;
        }

        medications.forEach(med => {
            if (!med.notification_times || !med.times) {
                return;
            }

            med.times.forEach(time => {
                const notificationTime = med.notification_times[time];
                if (!notificationTime) {
                    return;
                }

                const now = new Date();
                const notificationDate = new Date();
                notificationDate.setHours(notificationTime.hour, notificationTime.minute, 0, 0);

                // 오늘 알림 시간이 지났으면 내일로 설정
                if (notificationDate < now) {
                    notificationDate.setDate(notificationDate.getDate() + 1);
                }

                const timeUntilNotification = notificationDate.getTime() - now.getTime();

                // 알림 스케줄링
                setTimeout(() => {
                    const mealTime = time === '아침' ? '아침' : time === '점심' ? '점심' : '저녁';
                    const beforeAfter = med.before_meal ? '식사 전' : '식사 후';
                    
                    showNotification(
                        `${time} 약 시간`,
                        `${med.name}을(를) ${beforeAfter} 복용하세요.`,
                        {
                            tag: `medication-${med.id}-${time}`,
                            requireInteraction: true
                        }
                    );

                    // 매일 반복 (24시간마다)
                    setInterval(() => {
                        showNotification(
                            `${time} 약 시간`,
                            `${med.name}을(를) ${beforeAfter} 복용하세요.`,
                            {
                                tag: `medication-${med.id}-${time}`,
                                requireInteraction: true
                            }
                        );
                    }, 24 * 60 * 60 * 1000); // 24시간
                }, timeUntilNotification);
            });
        });
    }

    // 페이지 로드 시 알림 권한 요청 및 스케줄 설정
    window.addEventListener('DOMContentLoaded', async () => {
        const hasPermission = await requestNotificationPermission();
        if (hasPermission) {
            scheduleMedicationNotifications();
        }
    });

    // 전역 함수로 export
    window.MedicationNotification = {
        requestPermission: requestNotificationPermission,
        show: showNotification,
        schedule: scheduleMedicationNotifications
    };
})();

