(function() {
    const chatMessages = document.getElementById('chatMessages');
    const messageInput = document.getElementById('messageInput');
    const micButton = document.getElementById('micButton');
    const sendButton = document.getElementById('sendButton');

    // 스크롤을 맨 아래로 이동
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // 사용자 메시지 추가
    function addUserMessage(text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message user';
        
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        bubble.textContent = text;
        
        messageDiv.appendChild(bubble);
        chatMessages.appendChild(messageDiv);
        scrollToBottom();
    }

    // 타이핑 인디케이터 추가
    function addTypingIndicator() {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot';
        messageDiv.id = 'typingIndicator';
        
        const indicator = document.createElement('div');
        indicator.className = 'typing-indicator';
        
        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('div');
            dot.className = 'typing-dot';
            indicator.appendChild(dot);
        }
        
        messageDiv.appendChild(indicator);
        chatMessages.appendChild(messageDiv);
        scrollToBottom();
    }

    // 타이핑 인디케이터 제거
    function removeTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        if (indicator) {
            indicator.remove();
        }
    }

    // 봇 메시지 추가
    function addBotMessage(text) {
        removeTypingIndicator();
        
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot';
        
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        bubble.textContent = text;
        
        messageDiv.appendChild(bubble);
        chatMessages.appendChild(messageDiv);
        scrollToBottom();
    }

    // 백엔드 API URL 설정 (config.js에서 가져오거나 기본값 사용)
    const API_BASE_URL = (typeof API_CONFIG !== 'undefined' && API_CONFIG.BASE_URL) || 'http://localhost:5001/api';
    
    // GPT API를 사용한 챗봇 응답 생성
    async function getBotResponse(userMessage) {
        try {
            const response = await fetch(`${API_BASE_URL}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: userMessage
                })
            });
            
            if (!response.ok) {
                throw new Error('서버 응답 오류');
            }
            
            const data = await response.json();
            let responseText = data.response || '죄송합니다. 응답을 생성할 수 없습니다.';
            // 마크다운 제거 및 줄바꿈 정리
            responseText = responseText.replace(/\*\*/g, '').replace(/\*/g, '').replace(/_/g, '');
            responseText = responseText.replace(/\n{3,}/g, '\n\n');  // 3개 이상 줄바꿈을 2개로
            return responseText;
        } catch (error) {
            console.error('챗봇 API 오류:', error);
            // API 오류 시 기본 응답
            return '죄송합니다. 서버에 연결할 수 없습니다. 잠시 후 다시 시도해주세요.';
        }
    }

    // 메시지 전송 처리
    async function sendMessage() {
        const message = messageInput.value.trim();
        if (!message) return;

        // 사용자 메시지 추가
        addUserMessage(message);
        messageInput.value = '';

        // 타이핑 인디케이터 표시
        addTypingIndicator();

        // GPT API를 통한 봇 응답
        try {
            const botResponse = await getBotResponse(message);
            addBotMessage(botResponse);
        } catch (error) {
            console.error('메시지 전송 오류:', error);
            addBotMessage('죄송합니다. 오류가 발생했습니다. 잠시 후 다시 시도해주세요.');
        }
    }

    // 입력창 엔터 키 처리
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // 전송 버튼 클릭 처리 함수
    function handleSendButton(e) {
        if (e) {
            e.preventDefault();
            e.stopPropagation();
        }
        sendMessage();
        return false;
    }

    // 전송 버튼 이벤트 (모바일/데스크톱 모두 지원)
    sendButton.addEventListener('click', handleSendButton, { passive: false });
    sendButton.addEventListener('touchend', handleSendButton, { passive: false });
    sendButton.addEventListener('touchstart', (e) => {
        // touchstart에서도 처리하여 더 빠른 반응
        e.preventDefault();
    }, { passive: false });

    // 음성 인식 기능
    let recognition = null;
    let isListening = false;

    // Web Speech API 지원 확인 및 초기화
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.lang = 'ko-KR';
        recognition.continuous = false;
        recognition.interimResults = true; // 실시간 결과 표시

        recognition.onresult = (event) => {
            let interimTranscript = '';
            let finalTranscript = '';

            // 실시간 결과와 최종 결과 분리
            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += transcript;
                } else {
                    interimTranscript += transcript;
                }
            }

            // 실시간으로 입력 필드 업데이트
            if (finalTranscript) {
                messageInput.value = finalTranscript;
                isListening = false;
                micButton.classList.remove('listening');
            } else if (interimTranscript) {
                messageInput.value = interimTranscript;
            }
        };

        recognition.onerror = (event) => {
            console.error('음성 인식 오류:', event.error);
            isListening = false;
            micButton.classList.remove('listening');
            if (event.error === 'not-allowed') {
                alert('마이크 권한이 필요합니다. 브라우저 설정에서 마이크 권한을 허용해주세요.');
            }
        };

        recognition.onend = () => {
            isListening = false;
            micButton.classList.remove('listening');
        };
    }

    // 마이크 버튼 클릭
    micButton.addEventListener('click', () => {
        if (!recognition) {
            alert('이 브라우저는 음성 인식을 지원하지 않습니다.');
            return;
        }

        if (isListening) {
            // 이미 듣고 있으면 중지
            recognition.stop();
            isListening = false;
            micButton.classList.remove('listening');
        } else {
            // 음성 인식 시작
            try {
                recognition.start();
                isListening = true;
                micButton.classList.add('listening');
            } catch (error) {
                console.error('음성 인식 시작 오류:', error);
                isListening = false;
                micButton.classList.remove('listening');
            }
        }
    });

    // 초기 환영 메시지
    window.addEventListener('DOMContentLoaded', () => {
        setTimeout(() => {
            addTypingIndicator();
            setTimeout(() => {
                addBotMessage('안녕하세요! 약을먹자 챗봇입니다. 약 복용, 복약 내역 등에 대해 질문해주세요.');
            }, 1000);
        }, 500);
    });
})();

