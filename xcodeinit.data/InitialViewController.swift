//  Copyright © 2017 Axel Ancona Esselmann. All rights reserved.
//

import UIKit

class InitialViewModel {
    let title = "Hello World"
}

class InitialView: UIView {
    
    private let label = UILabel()
    
    init() {
        super.init(frame: CGRect.zero)
        backgroundColor = .blue
        
        createLayoutConstraints()
    }
    
    required init?(coder aDecoder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
    
    private func createLayoutConstraints() {
        addSubview(label)
        
        let left = NSLayoutConstraint(item: label, attribute: .leading, relatedBy: .equal, toItem: self, attribute: .leading, multiplier: 1.0, constant: 0.0)
        
        let right = NSLayoutConstraint(item: label, attribute: .trailing, relatedBy: .equal, toItem: self, attribute: .trailing, multiplier: 1.0, constant: 0.0)
        
        let top = NSLayoutConstraint(item: label, attribute: .top, relatedBy: .equal, toItem: self, attribute: .topMargin, multiplier: 1.0, constant: 0.0)
        
        label.translatesAutoresizingMaskIntoConstraints = false
        
        NSLayoutConstraint.activate([left, right, top])
    }
    
    func set(title: String) {
        label.text = title
    }
}

class InitialViewController: UIViewController {
    
    let viewModel: InitialViewModel
    
    init(viewModel: InitialViewModel) {
        self.viewModel = viewModel
        super.init(nibName: nil, bundle: nil)
        view = InitialView()
        
        updateView()
    }
    
    private func updateView() {
        guard let view = view as? InitialView else {
            assertionFailure("View not of type InitialView")
            return
        }
        view.set(title: viewModel.title)
    }
    
    required init?(coder aDecoder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
}

class MainNavigationController: UINavigationController {
    override func pushViewController(_ viewController: UIViewController, animated: Bool) {
        super.pushViewController(viewController, animated: animated)
        if viewController is InitialViewController {
            setNavigationBarHidden(true, animated: true)
        }
    }
}
