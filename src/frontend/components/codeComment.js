const CODE_COMMENT_STATUS = {
  OPENED: 0,
  CLOSED: 1,
};

export default class CodeComment {
  constructor(
    containerElement,
    parentElement,
    codeBlockId,
    status,
    comments = [],
  ) {
    this.containerElement = containerElement;
    this.parentElement = parentElement;
    this.codeBlockId = codeBlockId;
    this.status = status;
    this.comments = comments;
  }

  static _timePassedFormatting(timestampInSeconds) {
    const timeDiffInSeconds = (Date.now() / 1000) - timestampInSeconds;

    if (timeDiffInSeconds > 604800) {
      return 'more than a week ago';
    }
    if (timeDiffInSeconds > 86400) {
      return `${Math.round(timeDiffInSeconds / 86400)} days ago`;
    }
    if (timeDiffInSeconds > 3600) {
      return `${Math.round(timeDiffInSeconds / 3600)} hours ago`;
    }
    if (timeDiffInSeconds > 60) {
      return `${Math.round(timeDiffInSeconds / 60)} minutes ago`;
    }

    return 'less than a minute ago';
  }

  _getCommentsAsHtmlStr(comments) {
    return comments.map(comment => `
      <div class='code-block-single-comment m-1'>
        <div class="col-12 code-comment-header">
          <span>${comment.author}</span>
          <span class="float-right">${CodeComment._timePassedFormatting(comment.updatedAt)}</span>
        </div>
        <div class="col-12 code-comment-done-text">${comment.comment}</div>
      </div>`).join('');
  }

  template() {
    if (this.status === CODE_COMMENT_STATUS.OPENED) {
      return `
        <div class='container code-comment-container'>
          ${this.comments.length > 0 ? this._getCommentsAsHtmlStr(this.comments) : ''}
          <div class="row">
            <div class="col-12">
              <textarea class="code-comment-text" value=""></textarea>
            </div>
            <div class="col-2">
              <button class='save-code-comment-btn btn btn-light'>Save</button>
            </div>
          </div>
        </div>
      `;
    }

    return `<div class='container code-comment-container code-comment--closed'>
      ${this._getCommentsAsHtmlStr(this.comments)}
      </div>`;
  }

  addComment(comment) {
    this.comments.push({
      author: 'Me',
      comment,
      updatedAt: (Date.now() / 1000),
    });
    this.status = CODE_COMMENT_STATUS.CLOSED;
    this.render();
  }

  open() {
    this.status = CODE_COMMENT_STATUS.OPENED;
    this.render();
  }

  close() {
    if (this.comments.length === 0) {
      // no comments in this code block -> just remove it from UI
      this.parentElement.removeChild(this.containerElement);
    } else {
      this.status = CODE_COMMENT_STATUS.CLOSED;
    }
    this.render();
  }

  render() {
    this.containerElement.innerHTML = this.template();
  }

  static createNew(parentElement, codeBlockId) {
    const containerElement = document.createElement('div');
    parentElement.appendChild(containerElement);

    const codeComment = new CodeComment(
      containerElement,
      parentElement,
      codeBlockId,
      CODE_COMMENT_STATUS.OPENED,
    );

    codeComment.render();

    return codeComment;
  }

  static createExisting(parentElement, codeBlockId, comments) {
    const containerElement = document.createElement('div');
    parentElement.appendChild(containerElement);

    const codeComment = new CodeComment(
      containerElement,
      parentElement,
      codeBlockId,
      CODE_COMMENT_STATUS.CLOSED,
      comments,
    );

    codeComment.render();

    return codeComment;
  }
}
