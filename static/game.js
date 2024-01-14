class DomUtils {
    static showElement(selector, displayStyle = 'block') {
        const element = document.querySelector(selector);
        if (element) element.style.display = displayStyle;
    }

    static hideElement(selector) {
        const element = document.querySelector(selector);
        if (element) element.style.display = 'none';
    }

    static setTextContent(id, newText) {
        const element = document.getElementById(id);
        if (element) {
            // check whether the content has changed
            const oldText = element.textContent.toString().trim();
            const trimmedNewText = newText.toString().trim();

            if (oldText !== trimmedNewText) {
                element.textContent = trimmedNewText;
                element.textContent = newText;
                element.classList.add('updated');

                setTimeout(() => {
                    element.classList.remove('updated');
                }, 3000);  // recover after 3s
            }
        }
    }

    static createElement(type, properties = {}) {
        const element = document.createElement(type);
        Object.keys(properties).forEach(key => {
            element[key] = properties[key];
        });
        return element;
    }

    static disableButton(selector) {
        const button = document.querySelector(selector);
        if (button) {
            button.disabled = true;
        }
    }

    static enableButton(selector) {
        const button = document.querySelector(selector);
        if (button) {
            button.disabled = false;
        }
    }

    static disableButtonsInContainer(containerSelector) {
        const buttons = document.querySelectorAll(`${containerSelector} button`);
        buttons.forEach(button => {
            button.disabled = true;
        });
    }

    static enableButtonsInContainer(containerSelector) {
        const buttons = document.querySelectorAll(`${containerSelector} button`);
        buttons.forEach(button => {
            button.disabled = false;
        });
    }
}

class ApiService {
    static async fetchJSON(url, options = {}) {
        try {
            const response = await fetch(url, options);
            if (response.ok) {
                return await response.json();
            } else {
                throw new Error(`HTTP error: ${response.status}`);
            }
        } catch (error) {
            console.error(`Could not fetch ${url}: ${error}`);
            throw error;
        }
    }

    static async fetchStream(url, options = {}, callback) {
        try {
            const response = await fetch(url, options);
            if (!response.ok) {
                throw new Error(`HTTP error: ${response.status}`);
            }

            const reader = response.body.getReader();
            let cache_string = "";

            while (true) {
                const { done, value } = await reader.read();
                if (done) {
                    break;
                }
                const text = new TextDecoder().decode(value);
                cache_string += text;
                if (callback && typeof callback === 'function') {
                    callback(cache_string);
                }
            }
        } catch (error) {
            console.error(`Could not fetch ${url}: ${error}`);
            throw error;
        }
    }
}

class TextDisplay {
    constructor(text, container, interval) {
        this.text = text;
        this.container = container;
        this.interval = interval;
        this.currentIndex = 0;
    }

    display(callback) {
        const nextLetter = () => {
            if (this.currentIndex < this.text.length) {
                this.container.textContent += this.text.charAt(this.currentIndex);
                this.currentIndex++;
                setTimeout(nextLetter, this.interval);
            } else if (typeof callback === 'function') {
                callback();
            }
        };
        nextLetter();
    }
}

class Game {
    constructor() {
        //获取绘画标识符
        this.sessionId = localStorage.getItem('session_id');
        console.log(this.sessionId)
        this.md = window.markdownit();
        //获取背景按钮并添加点击事件监听器
        this.backgroundButton = document.querySelector('#backgroundButton');
        this.backgroundButton.addEventListener('click', () => {
            this.getBackground();
        });
        //获取事件按钮并添加点击事件监听器
        this.eventButton = document.querySelector('#eventButton');
        this.eventButton.addEventListener('click', () => {
            //故事推进
            this.getEpoch();
        });
    }

    async init() {
        console.log('init begin!')
        DomUtils.showElement('.begin');
        DomUtils.hideElement('#start-button');
        DomUtils.hideElement('.game');
        this.generateOpening();
    }

    //初始化一个角色
    async initPlayer() {
        try {
            await ApiService.fetchJSON('/life-reload/init/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ session_id: this.sessionId })
            });
            await this.updatePlayerData();
        } catch (error) {
            console.error('Error initializing player:', error);
        }
    }

    //开始游戏
    generateOpening() {
        const textContainer = document.getElementById('opening');
        console.log('opening!');
        const text = "欢迎来到《人生重启模拟器》，一个简约的世界，等待你来编织命运。在这里，每个选择都是重生的机会，每个对话都能开辟生活的新路径。用你的智慧探索无数可能，用你的决定定义未来。现在，深呼吸，按下“开始游戏”，让我们一起探索人生的无限可能吧！";
        const textDisplay = new TextDisplay(text, textContainer, 25);
        textDisplay.display(() => {
            DomUtils.showElement('#start-button', 'inline');
            const startButton = document.getElementById('start-button');
            startButton.addEventListener('click', () => {
                this.beginGame();
            });
        });
    }

    //转换成正常界面
    async beginGame() {
        console.log('opening!');
        DomUtils.hideElement('.begin');
        DomUtils.showElement('.game');
        await this.initPlayer();
        const cocoInput = document.getElementById('coco');
        const customButton = document.getElementById('customButton');
            customButton.addEventListener('click', () => {
                DomUtils.disableButton('#customButton');
                console.log('-----get success-----');
                console.log(cocoInput.value);
                this.sendInfomation(cocoInput.value);
                // this.getBackground();
            });
    }

    //发送信息
    async sendInfomation(message){
        try {
            //发送
            await ApiService.fetchStream('/life-reload/send_info/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ session_id: this.sessionId, message:message})
            });
        } catch (error) {
            console.error('Error fetching background:', error);
        }
    }

    //正常游戏界面
    async getBackground() {
        console.log('getfirstbackground!');
        DomUtils.disableButton('#backgroundButton');
        DomUtils.disableButton('#eventButton');
        try {
            //生成游戏背景
            await ApiService.fetchStream('/life-reload/begin/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ session_id: this.sessionId })
            }, this.displayMarkdown.bind(this));
        } catch (error) {
            console.error('Error fetching background:', error);
        }
        DomUtils.enableButton('#backgroundButton');
        DomUtils.enableButton('#eventButton');
    }

    //获取事件
    async getEvent() {
        try {
            await ApiService.fetchStream('/life-reload/event/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ session_id: this.sessionId })
            }, this.displayMarkdown.bind(this));
        } catch (error) {
            console.error('Error fetching event:', error);
        }
    }

    async getEnding() {
        try {
            await ApiService.fetchStream('/life-reload/ending/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ session_id: this.sessionId })
            }, this.displayMarkdown.bind(this));
        } catch (error) {
            console.error('Error fetching ending:', error);
        }
    }

    async getEval(optionNumber) {
        DomUtils.disableButton('#backgroundButton');
        DomUtils.disableButton('#eventButton');
        DomUtils.disableButtonsInContainer('#option-container');

        try {
            await ApiService.fetchStream('/life-reload/evaluation/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    selection: optionNumber
                })
            }, this.displayMarkdown.bind(this));
        } catch (error) {
            console.error('Error during evaluation:', error);
        } finally {
            DomUtils.enableButton('#backgroundButton');
            DomUtils.enableButton('#eventButton');
        }
    }

    //游戏流程推进控制器
    async getEpoch() {
        this.updatePlayerData();
        DomUtils.disableButton('#backgroundButton');
        DomUtils.disableButton('#eventButton');
        try {
            const isAlive = await this.checkIfAlive();
            if (!isAlive) {
                await this.getEnding();
                DomUtils.enableButton('#backgroundButton');
                return;
            }
            await this.getEvent();
            // parse event content and option content
            this.getParsedEvent();

        } catch (error) {
            console.error('Error in life event:', error);
        }
        DomUtils.enableButton('#backgroundButton');
        DomUtils.enableButton('#eventButton');
    }

    async checkIfAlive() {
        try {
            const data = await ApiService.fetchJSON('/life-reload/is_alive/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ session_id: this.sessionId })
            });
            return data;
        } catch (error) {
            console.error('Error checking if alive:', error);
            return false;
        }
    }

    //获取事件和选项
    getParsedEvent() {
        ApiService.fetchJSON('/life-reload/parsed_event/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ session_id: this.sessionId })
        })
        .then(data => {
            let eventValue = data.event;
            let optionValue = data.option;
            this.displayMarkdown(eventValue);
            //生成按钮
            this.generateButtons(optionValue);
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        })
        .finally(() => {
            DomUtils.enableButton('#backgroundButton');
            DomUtils.enableButton('#eventButton');
        });
    }

    //更新用户的信息
    async updatePlayerData() {
        try {
            const data = await ApiService.fetchJSON('/life-reload/get_person/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ session_id: this.sessionId })
            });
            if (data) {
                console.log(data);
                DomUtils.setTextContent('city', data["城市"]);
                DomUtils.setTextContent('position', data["职位"]);
                DomUtils.setTextContent('company', data["公司"]);
                DomUtils.setTextContent('age', data["年龄"]);
                DomUtils.setTextContent('charm', data["属性"]["魅力"]);
                DomUtils.setTextContent('intelligence', data["属性"]["智力"]);
                DomUtils.setTextContent('health', data["属性"]["健康"]);
                DomUtils.setTextContent('wealth', data["属性"]["富裕"]);
                DomUtils.setTextContent('happiness', data["属性"]["幸福度"]);
                DomUtils.showElement('.card', 'flex');
            }
        } catch (error) {
            console.error('Error update player:', error);
        }
    }

    //将传入的markdown文本显示在网页上
    displayMarkdown(markdownText) {
        const resultParagraph = document.getElementById("markdownArea");
        resultParagraph.innerHTML = this.md.render(markdownText);
        let container = document.querySelector('.markdown-container');
        container.scrollTop = container.scrollHeight;
    }

    //生成按钮
    generateButtons(inputStr) {
        const markdownContainer = document.getElementById("markdownArea");
        let optionContainer = document.getElementById("option-container");

        if (!optionContainer) {
            optionContainer = document.createElement('div');
            optionContainer.id = 'option-container';
            markdownContainer.appendChild(optionContainer);
        } else {
            optionContainer.innerHTML = '';
        }

        const regex = /(\d+\.)[^0-9]*(?=\d+\.|$)/g;
        const matches = inputStr.match(regex);

        if (matches) {
            matches.forEach((option, index) => {
                const btn = document.createElement("button");
                btn.innerHTML = this.strongText(option.trim());
                btn.onclick = () => this.getEval(index + 1);
                optionContainer.appendChild(btn);
            });

            markdownContainer.scrollTop = markdownContainer.scrollHeight;
        }
    }

    strongText(text) {
        return text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    }
}

window.onload = function() {
    checkAndUpdateCSS();
    const game = new Game();
    game.init();
}

async function checkAndUpdateCSS() {
    const url = '/life-reload/static/game.css'
    const cssLink = document.querySelector(`link[href="${url}"]`);
    if (!cssLink) return;

    try {
        const response = await fetch(url, { method: 'HEAD' });
        const newLastModified = response.headers.get('Last-Modified');
        const currentLastModified = cssLink.getAttribute('data-last-modified');

        if (newLastModified !== currentLastModified) {
            cssLink.href = `${url}?t=${new Date().getTime()}`;
            cssLink.setAttribute('data-last-modified', newLastModified);
        }
    } catch (error) {
        console.error('Error checking CSS update:', error);
    }
}
