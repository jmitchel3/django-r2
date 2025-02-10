/** @jsxRuntime classic */
/** @jsx h */
/** @jsxFrag Fragment */

import { h, Fragment, render } from 'preact';
import { FileUpload } from './FileUpload';

document.addEventListener('DOMContentLoaded', () => {
    const container = document.querySelector('#django-r2-uploader');
    if (container) {
        let dataset = container.dataset
        render(<FileUpload  {...dataset} />, container);
    }  
});